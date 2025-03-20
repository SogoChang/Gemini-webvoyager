from prompts import BRAIN_PROMPT, DEMO_PROMPT
import subprocess
import sys
import argparse
from google import genai
from google.genai import types
import re
import json
import time
import os
from time import sleep

def use_gemini_webvoyager(task_path, api_key):
    result = subprocess.run([sys.executable, "run.py", f"--test_file={task_path}", f"--api_key={api_key}"], capture_output=True, text=True, encoding='utf-8')
    return result

def extract_information(text):
    patterns = {
        "query": r"Query[; ]+\{([^}]*)\}",
        "ask": r"Ask[; ]+\[?(.[^\]]*)\]?",
        "answer": r"Answer[; ]+\[?(.[^\]]*)\]?"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            if key == "ask":
                return key, match.group(1)
            elif key == "answer":
                return key, match.group(1)
            else:
                return key, match.group(1)
    return None, None

def ask_action(content):
    text = input(content)
    return text

def print_message(object, save_dir=None):
    if save_dir:
        with open(os.path.join(save_dir, 'interact_messages.txt'), 'w', encoding='utf-8') as fw:
            fw.write(object)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, help="YOUR_API_KEY")
    args = parser.parse_args()

    current_time = time.strftime("%Y%m%d_%H_%M_%S", time.localtime())
    result_dir = os.path.join('brain_results', current_time)
    os.makedirs(result_dir, exist_ok=True)

    pattern = r'Thought:|Action:'
    history_messages = ""
    api_key=args.api_key
    while True:
        gemini_client = genai.Client(api_key=api_key)

        response = gemini_client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=history_messages,
                        config = types.GenerateContentConfig(
                            max_output_tokens=1000,
                            temperature=0.5,
                            system_instruction=BRAIN_PROMPT
                        )
                    )
        print(response.text)
        sleep(6)
        try:
            assert 'Thought:' in response.text and 'Action:' in response.text
        except AssertionError as e:
            fail_obs = "Format ERROR: Both 'Thought' and 'Action' should be included in your reply."
        history_messages += "{role: assistant, content: " + response.text + "}\n" 
        chosen_action = re.split(pattern, response.text)[2].strip()

        key, content = extract_information(chosen_action)
        if key == 'query':
            with open("data/test.jsonl", "w", encoding="utf-8") as f:
                content = '{'+content+'}'
                json_line = json.dumps(json.loads(content), ensure_ascii=False)
                f.write(json_line)
            query_response = use_gemini_webvoyager(task_path="data/test.jsonl", api_key=api_key)
            if query_response.stderr != '':
                print(query_response.stderr)
                break
            history_messages += "{role: query, content: " + query_response.stdout + "}\n"
            print_message(history_messages, result_dir)
        elif key == 'ask':
            reply = ask_action(content)
            history_messages += "{role: user, content: " + reply + "}\n"
            print_message(history_messages, result_dir)
        else:
            print(key)
            print(content)
            history_messages += "{role: answer, content: " + content + "}\n"
            print_message(history_messages, result_dir)
            break