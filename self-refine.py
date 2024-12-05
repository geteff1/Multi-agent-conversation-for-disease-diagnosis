import os
import time
import json
import argparse
import re
import pandas as pd

from typing import List, Dict, Optional, Union

import os.path as osp
from tqdm import tqdm
from functools import wraps

from autogen.io import IOStream
from autogen.formatting_utils import colored
from autogen import ConversableAgent, config_list_from_json
from autogen.agentchat.utils import gather_usage_summary
from autogen.code_utils import content_str
from medcs.dataset import MedDataset

class Prompt:
    def __init__(
        self,
        question_prefix: str,
        answer_prefix: str,
        intra_example_sep: str,
        inter_example_sep: str,
        engine: str = None,
        temperature: float = None,
    ) -> None:
        self.question_prefix = question_prefix
        self.answer_prefix = answer_prefix
        self.intra_example_sep = intra_example_sep
        self.inter_example_sep = inter_example_sep
        self.engine = engine
        self.temperature = temperature

    def make_query(self, prompt: str, question: str) -> str:
        return (
            f"{prompt}{self.question_prefix}{question}{self.intra_example_sep}{self.answer_prefix}"
        )


class ResponseGenTaskInit(Prompt):
    def __init__(self, engine: str) -> None:
        super().__init__(
            question_prefix="Conversation history: ",
            answer_prefix="Response: ",
            intra_example_sep="\n\n",
            inter_example_sep="\n\n###\n\n",
        )
        
        self.stage = engine


    def make_query(self, context: str) -> str:
        if self.stage == "inital":
            query = """
            Patient Presentation:
            {}

            Output in the following JSON format:
                                        ```json
                                        {{
                                            "Most Likely Diagnosis": "[current consensus on most likely diagnosis]",
                                            "Differential Diagnosis": "[current list of differential diagnoses]",
                                            "Recommended Tests": "[current consensus on recommended diagnostic tests]",
                                        }}
                                        ```."""
        else:
            query = """
            Patient Presentation:
            {}

            Output in the following JSON format:
                                        ```json
                                        {{
                                            "Most Likely Diagnosis": "[current consensus on most likely diagnosis]",
                                            "Differential Diagnosis": "[current list of differential diagnoses]",
                                        }}
                                        ```."""
        query = query.format(context)
        message = [{"content": query, "role": "user"}]
        return message

    def __call__(self, agent, context: str) -> str:
        message = self.make_query(context)
        # import pdb;pdb.set_trace()
        generated_response = agent.generate_reply(message)
        generated_response = content_str(generated_response)
        return generated_response



class ResponseGenFeedback(Prompt):
    def __init__(self, engine: str) -> None:
        super().__init__(
            question_prefix="",
            answer_prefix="",
            intra_example_sep="\n\n",
            inter_example_sep="\n\n###\n\n",
        )
        self.stage = engine

    def __call__(self, agent, context: str, response: str):
        message = self.get_prompt_with_question(context=context, response=response)
        generated_response = agent.generate_reply(message)
        generated_feedback = content_str(generated_response)
        generated_feedback = parse_json(generated_feedback)

        return generated_feedback

    def get_prompt_with_question(self, context: str, response: str):
        context = context.replace('System: ', '').replace('User: ', '')
        query = self.make_query(context=context, response=response)

        message = [{"content": query, "role": "user"}]
        return message

    def make_query(self, context: str, response: str):
        if self.stage == "inital":
            query = """
            Patient Presentation:
            {context}

            Response: 
            {response}

            Based on the Patient Presentation, you should evaluate the corresponding score for the Response.
            Scoring Criteria:
            - 50: The diagnosis and recommended tests were suggested
            - 40: The suggestions included something very close, but not exact
            - 30: The suggestions included something closely related that might have been helpful
            - 20: The suggestions included something related, but unlikely to be helpful
            - 0: No suggestions close
            What would be the score based on these criteria?
            Be critical, always find mistake and be cautious with the score.
            The scores can be any integral between either two category, such as 5, 15, 25, 35, 45, 50.
            Provide brief explanation for your choice. Do not expand the explanation, do not use line breaks, and write it in one paragraph.
            Output the final answer in json: 
                ```json
                {{
                    "Score": "[numberic, 0~50]",
                    "Explanation": "[Words]",
                }}
                ```."""
        else:
            query = """
            Patient Presentation:
            {context}

            Response: 
            {response}

            Based on the Patient Presentation, you should evaluate the corresponding score for the Response.
            Scoring Criteria:
            - 50: The diagnosis was suggested
            - 40: The suggestions included something very close, but not exact
            - 30: The suggestions included something closely related that might have been helpful
            - 20: The suggestions included something related, but unlikely to be helpful
            - 0: No suggestions close
            What would be the score based on these criteria?
            Be critical, always find mistake and be cautious with the score.
            The scores can be any integral between either two category, such as 5, 15, 25, 35, 45, 50.
            Provide brief explanation for your choice. Do not expand the explanation, do not use line breaks, and write it in one paragraph.
            Output the final answer in json: 
                ```json
                {{
                    "Score": "[numberic, 0~50]",
                    "Explanation": "[Words]",
                }}
                ```."""
        query = query.format(context=context, response=response)

        return query




class ResponseGenTaskIterate(Prompt):
    def __init__(self, engine: str) -> None:
        super().__init__(
            question_prefix="",
            answer_prefix="",
            intra_example_sep="\n\n",
            inter_example_sep="\n\n###\n\n",
        )
        self.stage = engine

    def make_query(self, example_input):
        """Given a list of examples that are incrementally improving, return a new example.
        """
        
        instr = """We want to iteratively improve the provided responses. To help improve, suggestion for each response on desired traits are provided: 1) Score, 2) Explanation.

        """
        if self.stage == "inital":

            template = """Conversation history: 
            {history}

            Output in the following JSON format:
                                            ```json
                                            {{
                                            "Most Likely Diagnosis": "[current consensus on most likely diagnosis]",
                                            "Differential Diagnosis": "[current list of differential diagnoses]",
                                            "Recommended Tests": "[current consensus on recommended diagnostic tests]",
                                            }}
                                            ```.
            """     

        else:
            template = """
            {history}

            Output in the following JSON format:
                                            ```json
                                            {{
                                                "Most Likely Diagnosis": "[current consensus on most likely diagnosis]",
                                                "Differential Diagnosis": "[current list of differential diagnoses]",
                                            }}
                                            ```.
            """     
        
        prompt = template.format(
                    history=example_input,
                )
        
        query = instr + prompt
        return query.strip()


    def __call__(
        self,
        agent,
        responses_to_scores: Dict[str, str],
    ) -> str:
        example_input = self.make_input(
            responses_to_scores=responses_to_scores
        )
        transfer_query = self.make_query(example_input)
        message = [{"content": transfer_query, "role": "user"}]
        modelresponse = agent.generate_reply(message)
        modelresponse = content_str(modelresponse)  # Ensure it's a string

        return modelresponse


    def make_input(
        self,
        responses_to_scores: Dict[str, str],
    ) -> str:
        input_txt = ""
        for response, (context, score, explanation) in responses_to_scores.items():
            context = context.replace('System: ', '').replace('User: ', '')
            input_txt += self._make_input(
                context=context,
                response=response,
                score=score,
                explanation=explanation,
            )
        return input_txt


    def _make_input(
        self,
        context: str,
        response: str,
        score: str,
        explanation: str,
    ) -> str:
        context = context.replace('System: ', '').replace('User: ', '')
        input_txt = f"""Conversation history: 
            
            {context}

            Response: {response}

            Score: {score}

            Explanation: {explanation}

            Okay, let's use this feedback to improve the response.
            """

        return input_txt


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
        choices=["x_gpt35_turbo", "x_gpt4_turbo", "x_gpt4o", "llama3.1"],
        help="the llm models",
    )
    parser.add_argument(
        "--dataset_name",
        type=str,
        default="rare_disease_302",
        choices=["rare_disease_302", "rare_disease_150", "rare_disease_152"],
        help="choice different dataset",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
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
        choices=[1, 2, 3, 4, 5],
        help="choice different stages",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="output",
        help="log file",
    )
    args = parser.parse_args()

    return args


def load(data_path):
    with open(data_path, "r") as file:
        data = json.load(file)
    return data


def parse_json(text):
    # Unified handling of all possible markdown code block formats
    patterns = [
        r"```(?:json|JSON)\s*(.*?)\s*```",  # Match ```json or ```JSON
        r"```\s*(.*?)\s*```",               # Match regular ```
        r"({.*?})"                          # Match bare JSON objects
    ]
    
    # Try all pattern matches
    json_str = None
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            json_str = match.group(1).strip()
            break
    
    # If no pattern matches, try parsing the entire text
    if json_str is None:
        json_str = text.strip()
    
    try:
        # Clean up the string and parse JSON
        json_str = json_str.replace('\n', '')
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")


def simple_retry(max_attempts=100, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_attempts - 1:
                        print(
                            f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay} second..."
                        )
                        time.sleep(delay)
                    else:
                        print(
                            f"All {max_attempts} attempts failed. Last error: {str(e)}"
                        )
                        raise

        return wrapper

    return decorator


# @simple_retry(max_attempts=100, delay=1)
def process_single_case(
    args,
    output_dir,
    json_name,
    case_type,
    case_crl,
    presentation,
    message,
    case_name,
    model_config,
    task_init, 
    task_feedback, 
    task_iterate,
    n_model
    ):
    case_info = {}

    doctor_agent = ConversableAgent(
        "Doctor",
        llm_config=model_config,
        human_input_mode="NEVER",  # Never ask for human input.
    )

    feedback_agent = ConversableAgent(
        "Fed",
        llm_config=model_config,
        human_input_mode="NEVER",  # Never ask for human input.
    )

    context = message
    
    max_attempts = 4
    n_attempts = 0
    best_response = None
    responses_to_scores = dict()
    all_responses_to_scores = dict()

    best_score_so_far = 0
    reduce_window = 0
    

    iostream = IOStream.get_default()

    while n_attempts < max_attempts:
        if n_attempts == 0:
            response = task_init(agent=doctor_agent, context=context)
        else:
            response = task_iterate(agent=doctor_agent, responses_to_scores=responses_to_scores)

        # Ensure response is a string
        response_str = str(response)

        case_cost = gather_usage_summary([doctor_agent])["usage_including_cached_inference"]["total_cost"]
        total_tokens = gather_usage_summary([doctor_agent])["usage_including_cached_inference"][n_model]["total_tokens"]
        
        if total_tokens > 3000:
            reduce_window += 1
            if total_tokens > 3500:
                reduce_window += 1
    
        iostream.print(colored(doctor_agent.name, "yellow"), "response:", flush=True)
        iostream.print(colored(response_str, ), flush=True)
        iostream.print(colored("*" * 60, "light_cyan"), flush=True)
        iostream.print(colored("Costs: ", "yellow"), colored(case_cost, "red"), colored("Tokens: ", "yellow"), colored(total_tokens, "red"), flush=True)

        scores = task_feedback(agent=feedback_agent, context=context, response=response_str)

        case_cost = gather_usage_summary([doctor_agent])["usage_including_cached_inference"]["total_cost"]
        total_tokens = gather_usage_summary([doctor_agent])["usage_including_cached_inference"][n_model]["total_tokens"]
        
        iostream.print(colored(doctor_agent.name, "yellow"), "scores:", flush=True)
        iostream.print(colored(str(scores), ), flush=True)
        iostream.print(colored("*" * 60, "light_cyan"), flush=True)
        iostream.print(colored("Costs: ", "yellow"), colored(case_cost, "red"), colored("Tokens: ", "yellow"), colored(total_tokens, "red"), flush=True)

        score = int(scores["Score"])
        
        all_responses_to_scores[response_str] = {
            "n_attempts": n_attempts,
            "score": score,
            "explanation": scores["Explanation"],
            "context": context,
        }

        if score >= best_score_so_far:  # Only iterate over responses that are improving
            best_score_so_far = score
            best_response = response_str
            responses_to_scores[response_str] = (context, scores["Score"], scores["Explanation"])
        else:
            print(f"Score of {response_str} is {score}, which is less than the current best of {best_score_so_far}")
        n_attempts += 1

    # At the end, 'best_response' is a string.
    json_output = parse_json(best_response)

    case_info["Type"] = case_type
    case_info["Crl"] = case_crl
    case_info["Cost"] = case_cost
    case_info["Presentation"] = presentation
    case_info["Name"] = case_name
    case_info["Most Likely"] = json_output["Most Likely Diagnosis"]
    case_info["Other Possible"] = json_output["Differential Diagnosis"]

    if args.stage == "inital":
        case_info["Recommended Tests"] = json_output["Recommended Tests"]

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
    n_model = config_list[0]["model"]
    model_config = {
        "cache_seed": None,
        "temperature": args.temperature,
        "config_list": config_list,
        "timeout": 120,
    }

    dataset = MedDataset(dataname=args.dataset_name)

    data_len = len(dataset)

    for idx in tqdm(range(data_len)):

        (
            case_type,
            case_name,
            case_crl,
            case_initial_presentation,
            case_follow_up_presentation,
        ) = dataset[idx]

        json_name = f"{case_crl}.json"

        output_dir = osp.join(
            args.output_dir,
            "SELF_REFINE",
            args.stage,
            args.model_name,
            f"temp{str(args.temperature)}",
            str(args.times),
        )

        if not osp.exists(output_dir):
            os.makedirs(output_dir)

        file_names = os.listdir(output_dir)

        json_files = [file for file in file_names if file.endswith(".json")]

        if json_name in json_files:
            continue

        # Generation of the first response
        task_init = ResponseGenTaskInit(engine=args.stage)
        
        # Getting feedback
        task_feedback = ResponseGenFeedback(engine=args.stage)

        # Iteratively improving the response
        task_iterate = ResponseGenTaskIterate(engine=args.stage)

        if args.stage == "inital":
            presentation = case_initial_presentation
            message = """
            Here is a patient case for analysis, provide the final diagnosis, final differential diagnosis and recommended tests.
            {patient_history}""".format(
                patient_history=presentation
            )
        else:
            presentation = case_follow_up_presentation
            message = """
            Here is a patient case for analysis, provide the final diagnosis, final differential diagnosis.
            {patient_history}""".format(
                patient_history=case_follow_up_presentation
            )
  
        try:
            process_single_case(
                args,
                output_dir,
                json_name,
                case_type,
                case_crl,
                message,
                presentation,
                case_name,
                model_config,
                task_init, 
                task_feedback, 
                task_iterate,
                n_model
            )
        except Exception as e:
            print(f"Failed to process case {idx} after all attempts: {str(e)}")
            continue


if __name__ == "__main__":

    main()
