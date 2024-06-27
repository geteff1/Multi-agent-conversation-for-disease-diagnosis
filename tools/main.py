import os
import json
import argparse
import asyncio

import os.path as osp
from tqdm import tqdm

from metagpt.team import Team
from metagpt.logs import logger
from metagpt.config2 import Config
from metagpt.schema import Message
from metagpt.actions import UserRequirement
from metagpt.environment import Environment
from metagpt.const import MESSAGE_ROUTE_TO_ALL

from medcs.dataset import MedDataset

from medcs.role import Moderator, Analyst, Voter, Revisor
from medcs.enviroment import MedCSEnv
from medcs.team import MedTeam

from medcs.action import (
    Query,
    Analysis,
    Vote,
    SynthesizingReport,
    Revise,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Medagents Setting")
    parser.add_argument(
        "--model_name",
        type=str,
        default="openai-gpt-3.5-turbo",
        choices=["openai-gpt-4-turbo", "openai-gpt-3.5-turbo"],
        help="the llm models",
    )
    parser.add_argument(
        "--dataset_name",
        type=str,
        default="rare_disease_cases_150",
        choices=["rare_disease_cases_150", "rare_disease_cases_300"],
        help="choice different dataset",
    )
    parser.add_argument(
        "--method",
        type=str,
        default="syn_verif",
        choices=["syn_verif", "syn_only", "anal_only", "base_direct", "base_cot"],
        help="choice different methods",
    )
    parser.add_argument(
        "--stage",
        type=str,
        default="inital",
        choices=["inital", "follow_up"],
        help="choice different stages",
    )
    parser.add_argument(
        "--num_specialists", type=int, default=3, help="number of experts"
    )
    parser.add_argument("--n_round", type=int, default=2, help="attempt_vote")
    parser.add_argument("--output_dir", type=str, default="logs", help="log file")

    args = parser.parse_args()

    return args


# async def get_specialists(role, url):
#     attempts = 0
#     while attempts < 3:
#         try:
#             query_specialists = await role.run()
#             medical_specialists = (
#                 query_specialists.content.split(":")[-1].strip().split(" | ")
#             )
#             return medical_specialists
#         except Exception as e:
#             attempts += 1
#             print(f"Attempt {attempts}: Failed with error {e}")
#             if attempts == 3:
#                 return (
#                     f"Error: Failed to retrieve specialists after 3 attempts, in {url}"
#                 )


def transform_dict2text(presentation, specialists, analyses):

    report = ""
    i = 0
    for _specialist, _analysis in zip(specialists, analyses):
        report += (
            f"Report{i} \n"
            f"presentation: {presentation} \n"
            f"Specialist: {_specialist} \n"
            f"Analysis: {_analysis} \n\n"
        )
        i += 1

    return report


async def main():
    args = parse_args()
    model_name = f"{args.model_name}.yaml"
    config_path = osp.join("configs", model_name)
    llm_config = Config.from_home(config_path)
    query_llm_config = llm_config
    expert_llm_config = llm_config
    query_llm_config.llm.max_token = 50
    expert_llm_config.llm.max_token = 300

    task_name = f"{args.model_name}-{args.dataset_name}-{args.stage}--{args.num_specialists}--{args.n_round}"
    recorder_floder = osp.join(args.output_dir, task_name)

    if not osp.exists(recorder_floder):
        os.makedirs(recorder_floder)

    # import pdb;pdb.set_trace()
    dataset = MedDataset(dataname=args.dataset_name)

    data_len = len(dataset)

    total_cost = 0.0

    for idx in tqdm(range(data_len)):
        case_cost = 0.0
        case_info = {}

        (
            case_type,
            case_name,
            case_crl,
            case_initial_presentation,
            case_follow_up_presentation,
        ) = dataset[idx]

        if args.stage == "inital":
            case_presentation = case_initial_presentation
        elif args.stage == "follow_up":
            case_presentation = case_follow_up_presentation
        else:
            raise NotImplementedError

        ### 1. Query and Select Specialists
        # action
        query = Query(private_config=query_llm_config)
        # Role
        selector = Moderator(
            name="Selector",
            actions=[query],
            num_specialists=args.num_specialists,
        )

        logger.info(case_presentation)

        # TODO adding """try...except"""
        query_specialists = await selector.run(case_presentation)
        _specialists = query_specialists.content.split(":")[-1].strip().split(" | ")
        logger.info(_specialists)
        case_cost += selector.llm.cost_manager.total_cost

        ### 2. Specialists Discussion and Get inital Synthesizing Report

        #### 2.1 Specialists Discussion
        analysis_actions = []
        for idx, specialist in enumerate(_specialists):
            analysis = Analysis(private_config=expert_llm_config)
            analysis_actions.append(analysis)

        analysis_specialists = []
        for idx, specialist in enumerate(_specialists):
            actions = [analysis_actions[idx]]
            if idx == 0:
                watches = [UserRequirement, analysis_actions[-1]]
            else:
                watches = [UserRequirement, analysis_actions[idx - 1]]

            analys = Analyst(name=specialist, actions=actions, watches=watches)
            analysis_specialists.append(analys)

        analysis_env = MedCSEnv(desc="Rare Disease Analysis Env")
        analysis_env.add_announ(announ=case_presentation)
        analysis_env.add_role_list(role_list=_specialists)

        analysis_team = MedTeam(
            investment=10.0, env=analysis_env, roles=analysis_specialists
        )
        # for analysis_specialist in analysis_specialists:
        #     analysis_specialist.set_env(analysis_env)

        diag_env = await analysis_team.run(
            n_round=args.n_round * args.num_specialists,
            send_to=_specialists[0],
            idea="No History",
        )

        case_cost += analysis_team.cost_manager.total_cost

        diag_buffer = diag_env.diag_buffer.pop_all()
        last_loop_diags = diag_buffer[-args.num_specialists :]

        #### 2.2 Get inital Synthesizing Report
        anayses_text = transform_dict2text(
            presentation=case_presentation,
            specialists=_specialists,
            analyses=last_loop_diags,
        )

        synthereport = SynthesizingReport(private_config=llm_config)
        # Role
        synthesize = Moderator(
            name="Synthesize",
            actions=[synthereport],
            num_specialists=args.num_specialists,
        )

        syn_report = await synthesize.run(anayses_text)

        case_cost += synthesize.llm.cost_manager.total_cost

        ### 3. Voting, Advising and Revising
        #### 3.1 Voting and Advising
        num_try = 0
        hasno_flag = True
        all_vote_history = []
        
        while num_try < args.n_round and hasno_flag:
            vote_actions = []
            num_try += 1
            hasno_flag = False
            for idx, specialist in enumerate(_specialists):
                vote = Vote(private_config=expert_llm_config)
                vote_actions.append(vote)

            vote_specialists = []
            for idx, specialist in enumerate(_specialists):
                actions = [vote_actions[idx]]
                if idx == 0:
                    watches = [UserRequirement, vote_actions[-1]]
                else:
                    watches = [UserRequirement, vote_actions[idx - 1]]

                voter = Voter(name=specialist, actions=actions, watches=watches)
                vote_specialists.append(voter)

            vote_env = MedCSEnv(desc="Rare Disease Vote Env")
            vote_env.add_announ(announ=syn_report)
            vote_env.add_role_list(role_list=_specialists)

            vote_team = MedTeam(investment=10.0, env=vote_env, roles=vote_specialists)

            advice_env = await vote_team.run(
                n_round=args.num_specialists,
                send_to=_specialists[0],
                idea="No Massge",
            )

            vote_history = advice_env.vote_history
            all_vote_history.append(vote_history)
            revision_advice = advice_env.revision_advice
            if len(revision_advice) > 0:
                #### 3.2 Revising
                hasno_flag = True
                revise = Revise(private_config=llm_config)
                # Role
                revisor = Revisor(
                    name="Revisor",
                    actions=[revise],
                )
                msg = {"syn_report": syn_report, "revision_advice": revision_advice}
                syn_report = await revisor.run(msg)


        recoder_name = f"{case_crl}.json"
        recorder_path = osp.join(recorder_floder, recoder_name)

        with open(recorder_path, "w") as file:
            json.dump(case_info, file, indent=4)


if __name__ == "__main__":
    asyncio.run(
        main()
    )  # run as python debate.py --idea="TOPIC" --investment=3.0 --n_round=5
