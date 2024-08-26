import re
import time
import json

from functools import wraps


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
