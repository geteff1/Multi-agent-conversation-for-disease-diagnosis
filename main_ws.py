import os
import re
import time
import json
import argparse
from functools import wraps

import os.path as osp
from tqdm import tqdm

from autogen import (
    GroupChat,
    UserProxyAgent,
    ConversableAgent,
    AssistantAgent,
    GroupChatManager,
    config_list_from_json,
)

from utils import *




def parse_args():
    parser = argparse.ArgumentParser(description="Medagents Setting")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/config_list.json",
        help="the llm models' config file",
    )
    parser.add_argument(
        "--query_model_name",
        type=str,
        default="x_gpt4o",
        choices=["x_gpt35_turbo", "x_gpt4_turbo", "x_gpt4o"],
        help="the llm models",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="x_gpt35_turbo",
        choices=["x_gpt35_turbo", "x_gpt4_turbo", "x_gpt4o"],
        help="the llm models",
    )
    parser.add_argument(
        "--dataset_name",
        type=str,
        default="rare_disease_302",
        choices=["rare_disease_302"],
        help="choice different dataset",
    )
    parser.add_argument(
        "--stage",
        type=str,
        default="inital",
        choices=["inital", "follow_up"],
        help="choice different stages",
    )

    parser.add_argument(
        "--times",
        type=int,
        default=1,
        choices=[1, 2, 3],
        help="choice different stages",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="output",
        help="log file",
    )
    parser.add_argument(
        "--num_specialists", type=int, default=3, help="number of experts"
    )
    parser.add_argument("--n_round", type=int, default=13, help="attempt_vote")
    parser.add_argument("--query_round", type=int, default=1, help="query times")

    args = parser.parse_args()

    return args





@simple_retry(max_attempts=100, delay=1)
def process_single_case(
    args, dataset, idx, output_dir, model_config, query_model_config
):
    case_cost = 0.0
    case_info = {}

    (
        case_type,
        case_name,
        case_crl,
        case_initial_presentation,
        case_follow_up_presentation,
    ) = dataset[idx]

    json_name = f"{case_crl}.json"
    conversation_name = f"{case_crl}_conversation.json"
    identify = f"{args.num_specialists}-{args.n_round}"

    output_dir = osp.join(
        output_dir,
        "MAC_WS",
        args.stage,
        args.model_name,
        identify,
        str(args.times),
    )

    if not osp.exists(output_dir):
        os.makedirs(output_dir)

    file_names = os.listdir(output_dir)

    json_files = [file for file in file_names if file.endswith(".json")]

    if json_name in json_files and conversation_name in json_files:
        return

    if args.stage == "inital":
        case_presentation = case_initial_presentation
    elif args.stage == "follow_up":
        case_presentation = case_follow_up_presentation
    else:
        raise NotImplementedError

    coordinator = ConversableAgent(
        "Medical_Coordinator",
        system_message="You are a Medical Coordinator. Your role is to provide the patient's medical history and ask questions to determine the appropriate specialist. You should seek clarification and ensure all relevant information is covered.",
        llm_config=query_model_config,
        human_input_mode="NEVER",  # Never ask for human input.
    )

    consultant = ConversableAgent(
        "Senior_Medical_Consultant",
        system_message="You are a Senior Medical Consultant. Your role is to answer the Medical Coordinator's questions, recommend the appropriate specialist based on the medical history provided, and correct any misconceptions.",
        llm_config=query_model_config,
        human_input_mode="NEVER",  # Never ask for human input.
    )

    consultant_message = get_consultant_message(case_presentation, int(args.num_specialists))

    result = coordinator.initiate_chat(
        consultant, message=consultant_message, max_turns=args.query_round
    )
    top_k_specialists = prase_json(result.chat_history[-1]["content"])[
        "top_k_specialists"
    ]
    assert len(top_k_specialists) == args.num_specialists
    case_cost += result.cost["usage_including_cached_inference"]["total_cost"]

    Docs = []
    for specialist in top_k_specialists:
        name = specialist.replace(" ", "_")
        doc_system_message = get_doc_system_message(
            doctor_name=name, stage=args.stage)

        Doc = AssistantAgent(
            name=name,
            llm_config=model_config,
            system_message=doc_system_message,
        )
        Docs.append(Doc)


    supervisor_system_message = get_supervisor_system_message(
        stage=args.stage, use_specialist=True, specialists=top_k_specialists
    )

    Supervisor = AssistantAgent(
        name="Supervisor",
        llm_config=model_config,
        system_message=supervisor_system_message,
    )

    agents = Docs + [Supervisor]
    groupchat = GroupChat(
        agents=agents,
        messages=[],
        max_round=args.n_round,
        speaker_selection_method="auto",  #"auto" or "round_robin": 下一个发言者以循环方式选择，即按照agents中提供的顺序进行迭代.  效果不太理想，需要更改prompt
        admin_name="Critic",
        select_speaker_auto_verbose=False,
        allow_repeat_speaker=True,
        send_introductions=False,
        max_retries_for_selecting_speaker=args.n_round // (1 + args.num_specialists),
    )
    time.sleep(5)
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=model_config,
        is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    )

    inital_message = get_inital_message(patient_history=case_presentation, stage=args.stage)

    output = Supervisor.initiate_chat(
        manager,
        message=inital_message,
    )

    #case cost
    for agent in agents:
        case_cost += agent.client.total_usage_summary ['total_cost']
        
    # Save the complete conversation
    conversation_path = osp.join(output_dir, conversation_name)
    with open(conversation_path, "w") as file:
        json.dump(output.chat_history, file, indent=4)


    critic_output = [
        item
        for i, item in enumerate(output.chat_history)
        if item.get("name") == None
        and '"Most Likely Diagnosis":' in item.get("content")
    ]

    syn_report = critic_output[-1]["content"]

    json_output = prase_json(syn_report)

    case_info["Type"] = case_type
    case_info["Crl"] = case_crl
    case_info["Cost"] = case_cost
    case_info["Presentation"] = case_presentation
    case_info["Name"] = case_name
    case_info["Most Likely"] = json_output.get("Most Likely Diagnosis")
    case_info["Other Possible"] = json_output.get("Differential") or json_output.get(
        "Differential Diagnosis"
    )

    if args.stage == "inital":
        case_info["Recommend Tests"] = json_output.get(
            "Recommend Tests"
        ) or json_output.get("Recommended Tests")

    recorder_path = osp.join(output_dir, json_name)
    with open(recorder_path, "w") as file:
        json.dump(case_info, file, indent=4)


def main():
    args = parse_args()

    query_filter_criteria = {
        "tags": [args.query_model_name],
    }

    filter_criteria = {
        "tags": [args.model_name],
    }


    query_config_list = config_list_from_json(
        env_or_file=args.config, filter_dict=query_filter_criteria
    )

    config_list = config_list_from_json(
        env_or_file=args.config, filter_dict=filter_criteria
    )



    query_model_config = {
        "cache_seed": None,
        "temperature": 0,
        "config_list": query_config_list,
        "timeout": 120,
    }

    model_config = {
        "cache_seed": None,
        "temperature": 1,
        "config_list": config_list,
        "timeout": 300,
    }


    dataset = MedDataset(dataname=args.dataset_name)

    data_len = len(dataset)

    output_dir = args.output_dir

    for idx in tqdm(range(data_len)):
        try:
            process_single_case(
                args, dataset, idx, output_dir, model_config, query_model_config
            )
        except Exception as e:
            print(f"Failed to process case {idx} after all attempts: {str(e)}")
            continue


if __name__ == "__main__":
    main()
