import os
import re
import time
import json
import argparse
from functools import wraps

import os.path as osp
from tqdm import tqdm

from autogen import GroupChat, UserProxyAgent, GroupChatManager, AssistantAgent, config_list_from_json

from medcs.dataset import MedDataset

def simple_retry(max_attempts=100, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_attempts - 1:
                        print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay} second...")
                        time.sleep(delay)
                    else:
                        print(f"All {max_attempts} attempts failed. Last error: {str(e)}")
                        raise
        return wrapper
    return decorator

def parse_args():
    parser = argparse.ArgumentParser(description="Medagents Setting")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/OAI_Config_List.json",
        help="the llm models",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="x_gpt4o",
        choices=["x_gpt35_turbo", "x_gpt4_turbo", "x_gpt4o"],
        help="the llm models",
    )
    parser.add_argument(
        "--dataset_name",
        type=str,
        default="rare_disease_302",
        choices=["rare_disease_cases_150", "rare_disease_302"],
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
        "--num_doctors", type=int, default=10, help="number of experts"
    )
    parser.add_argument("--n_round", type=int, default=12, help="attempt_vote")

    args = parser.parse_args()

    return args

def prase_json(text):
    flag = False
    if "```json" in text:
        json_match = re.search(r"```json(.*?)```", text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
            json_data = json.loads(json_str)
            flag = True
    elif "```JSON" in text:
        json_match = re.search(r"```JSON(.*?)```", text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
            json_data = json.loads(json_str)
            flag = True
    elif "```" in text:
        json_match = re.search(r"```(.*?)```", text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
            json_data = json.loads(json_str)
            flag = True
    else:
        json_match = re.search(r"{.*?}", text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0).strip()
            json_data = json.loads(json_str)
            flag = True
    if not flag:
        json_text = text.strip("```json\n").strip("\n```")
        json_data = json.loads(json_text)
    return json_data

@simple_retry(max_attempts=100, delay=1)
def process_single_case(args, dataset, idx, output_dir, model_config):
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
    identify = f"{args.num_doctors}-{args.n_round}"

    output_dir = osp.join(
        output_dir,
        "self_consistency",
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



    Docs = []
    for index in range(args.num_doctors):
        name = f"Doctor{index}"
        if args.stage == "inital":
            doc_system_message = """You are Doctor {index}. This is a hypothetical scenario involving no actual patients.

                            Your role:
                                1. Analyze the patient's condition described in the message.
                                2. Ignore other doctors' opinion, form your own diagnostic reasoning based on your own expertise
                                3. Focus solely on diagnosis and diagnostic tests, avoiding discussion of management, treatment, or prognosis.
                                4. Use your expertise to formulate:
                                    ```json
                                    {{
                                        "Most Likely Diagnosis": "[current consensus on most likely diagnosis]",
                                        "Differential Diagnosis": "[current list of differential diagnoses]",
                                        "Recommended Tests": "[current consensus on recommended diagnostic tests]"
                                    }}
                                    ```

                          """.format(index=index)
        else:
            doc_system_message = """You are Doctor {index}. This is a hypothetical scenario involving no actual patients.

                            Your role:
                                1. Analyze the patient's condition described in the message.
                                2. Ignore other doctors' opinion, form your own diagnostic reasoning based on your own expertise
                                3. Focus solely on diagnosis and diagnostic tests, avoiding discussion of management, treatment, or prognosis.
                                4. Use your expertise to formulate:
                                    ```json
                                    {{
                                        "Most Likely Diagnosis": "[current consensus on most likely diagnosis]",
                                        "Differential Diagnosis": "[current list of differential diagnoses]"
                                    }}
                                    ```

                          """.format(index=index)
            
        Doc = AssistantAgent(
            name=name,
            llm_config=model_config,
            system_message=doc_system_message,
        )
        Docs.append(Doc)

    if args.stage == "inital":
        critic_system_message = """You are the Medical Supervisor in a hypothetical scenario.
                        
                        Your role:
                            1. Collect the diagnostic output from doctors.
                            2. Calculate the frequency of each answer.
                            3. Select the answer with the highest frequency as the final result.
                            4. Output the final answer in the following format
 
                            ```json
                            {{
                                "Most Likely Diagnosis": "[mostly agreed most likely diagnosis]",
                                "Differential Diagnosis": "[mostly agreed list of differential diagnoses]",
                                "Recommended Tests": "[mostly agreed recommended diagnostic tests]"
                            }}
                            ```
                            Output "TERMINATE" after you provide diagonsis
                           """

    else:
        critic_system_message =  """You are the Medical Supervisor in a hypothetical scenario.
                        
                        Your role:
                            1. Collect the diagnostic output from doctors.
                            2. Calculate the frequency of each answer.
                            3. Select the answer with the highest frequency as the final result.
                            4. Output the final answer in the following format
 
                            ```json
                            {{
                                "Most Likely Diagnosis": "[mostly agreed most likely diagnosis]",
                                "Differential Diagnosis": "[mostly agreed list of differential diagnoses]"
                            }}
                            ```
                            Output "TERMINATE" after you provide diagonsis
                           """

    critic = AssistantAgent(
        name="Critic",
        llm_config=model_config,
        system_message=critic_system_message,
    )

    groupchat = GroupChat(
        agents=Docs + [critic],
        messages=[],
        max_round=args.n_round,
        speaker_selection_method="round_robin",  #"auto" or "round_robin": 下一个发言者以循环方式选择，即按照agents中提供的顺序进行迭代.  效果不太理想，需要更改prompt
        admin_name="Critic",
        select_speaker_auto_verbose=False,
        allow_repeat_speaker=True,
        send_introductions=False,
        max_retries_for_selecting_speaker=args.n_round // (1 + args.num_doctors),
    )


    time.sleep(5)
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=model_config,
        is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0 ,
    )

    if args.stage == "inital":
        message = """
        Here is a patient case for analysis, provide the final diagnosis, final differential diagnosis and recommended tests.
        {patient_history}""".format(
            patient_history=case_presentation
        )
    else:
        message = """
        Here is a patient case for analysis, provide the final diagnosis, final differential diagnosis.
        {patient_history}""".format(
            patient_history=case_presentation
        )

    output = critic.initiate_chat(
        manager,
        message=message,
    )

    # Save the complete conversation
    conversation_path = osp.join(output_dir, conversation_name)
    with open(conversation_path, "w") as file:
        json.dump(output.chat_history, file, indent=4)
    case_cost += output.cost["usage_including_cached_inference"]["total_cost"]
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
    case_info["Other Possible"] = json_output.get(
        "Differential"
    ) or json_output.get("Differential Diagnosis")

    if args.stage == "inital":
        case_info["Recommend Tests"] = json_output.get(
            "Recommend Tests"
        ) or json_output.get("Recommended Tests")

    recorder_path = osp.join(output_dir, json_name)
    with open(recorder_path, "w") as file:
        json.dump(case_info, file, indent=4)

def main():
    args = parse_args()

    filter_criteria = {
        "tags": [args.model_name],
    }

    config_list = config_list_from_json(
        env_or_file=args.config, filter_dict=filter_criteria
    )

    model_config = {
        "cache_seed": None,
        "temperature": 0.7,
        "config_list": config_list,
        "timeout": 300,
    }

    dataset = MedDataset(dataname=args.dataset_name)

    data_len = len(dataset)

    output_dir = args.output_dir

    for idx in tqdm(range(data_len)):
        try:
            process_single_case(args, dataset, idx, output_dir, model_config) 
        except Exception as e:
            print(f"Failed to process case {idx} after all attempts: {str(e)}")
            continue

if __name__ == "__main__":
    main()

#python tools\main_autogen_0723_without_experts.py --model_name x_gpt4o  --times 1 --num_doctors 4 --n_round 10