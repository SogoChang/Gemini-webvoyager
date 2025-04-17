from prompts import BRAIN_PROMPT, DEMO_PROMPT, NEW_BRAIN_PROMPT
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
import io

def use_gemini_webvoyager(task_path, api_key, task):
    # Ensure UTF-8 encoding when writing to files
    with open(task_path, "w", encoding="utf-8") as f:
        if type(task) == str:
            task = '{'+task+'}'
            json_line = json.dumps(json.loads(task), ensure_ascii=False)
        else:
            json_line = json.dumps(task, ensure_ascii=False)
        f.write(json_line)
    
    # Use UTF-8 locale environment for subprocess
    my_env = os.environ.copy()
    if sys.platform.startswith('win'):
        my_env["PYTHONIOENCODING"] = "utf-8"
    
    result = subprocess.run(
        [sys.executable, "run_v2.py", f"--test_file={task_path}", f"--api_key={api_key}"], 
        capture_output=True, 
        text=False, 
        env=my_env
    )
    
    # Always decode with UTF-8, use 'replace' for any problematic characters
    stdout = result.stdout.decode('utf-8', errors='replace')
    stderr = result.stderr.decode('utf-8', errors='replace')
        
    class TextResult:
        pass
    
    text_result = TextResult()
    text_result.stdout = stdout
    text_result.stderr = stderr
    text_result.returncode = result.returncode
    
    return text_result

def extract_information(text):
    patterns = {
        "query": r"Query[; ]+\{([^}]*)\}",
        "ask": r"Ask[; ]+\[?(.[^\]]*)\]?",
        "answer": r"Answer[; ]+\[?(.[^\]]*)\]?",
        "attraction": r"Attraction[; ]+\[?(.[^\]]*)\]?",
        "finish": r"Finish[; ]+"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            if key == "ask":
                return key, match.group(1)
            elif key == "answer":
                return key, match.group(1)
            elif key == "attraction":
                return key, match.group(1)
            elif key == "finish":
                return key, None
            else:
                return key, match.group(1)
    return None, None

def ask_action(content):
    # Make sure the input prompt is displayed correctly
    if sys.platform.startswith('win'):
        try:
            print(content, end='', flush=True)
            return input()
        except UnicodeEncodeError:
            # Fallback for Windows console with encoding issues
            print(content.encode('utf-8', errors='replace').decode(sys.stdout.encoding, errors='replace'), end='', flush=True)
            return input()
    else:
        # For Unix systems, should work with UTF-8 by default
        return input(content)

def print_message(object, save_dir=None):
    if save_dir:
        with open(os.path.join(save_dir, 'interact_messages.txt'), 'w', encoding='utf-8') as fw:
            fw.write(object)

def use_attraction_agent(file_name, content, api_key):
    # Ensure content is properly encoded
    if isinstance(content, str):
        content = content.encode('utf-8', errors='replace').decode('utf-8')
    
    # Use UTF-8 locale environment for subprocess
    my_env = os.environ.copy()
    if sys.platform.startswith('win'):
        my_env["PYTHONIOENCODING"] = "utf-8"
    
    result = subprocess.run(
        [sys.executable, "attraction_v2.py", f"--file_name={file_name}", f"--api_key={api_key}", f"--content={content}"], 
        capture_output=True, 
        text=False,
        env=my_env
    )
    
    # Always decode with UTF-8, use 'replace' for any problematic characters
    stdout = result.stdout.decode('utf-8', errors='replace')
    stderr = result.stderr.decode('utf-8', errors='replace')
        
    class TextResult:
        pass
    
    text_result = TextResult()
    text_result.stdout = stdout
    text_result.stderr = stderr
    text_result.returncode = result.returncode
    
    return text_result

if __name__ == "__main__":
    # Configure for UTF-8 encoding in stdout/stderr
    if sys.platform.startswith('win'):
        # For Windows, try to set console to UTF-8 mode
        os.system("chcp 65001")
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    
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
                            system_instruction=NEW_BRAIN_PROMPT
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
            
            query_response = use_gemini_webvoyager(task_path="data/test.jsonl", api_key=api_key, task=content)
            if query_response.stderr != '':
                print(query_response.stderr)
                break
            history_messages += "{role: query, content: " + query_response.stdout + "}\n"
            print_message(history_messages, result_dir)
        elif key == 'ask':
            reply = ask_action(content)
            history_messages += "{role: user, content: " + reply + "}\n"
            print_message(history_messages, result_dir)
        elif key == 'attraction':
            file_name = f"{content}.json"
            attraction_folder = "attraction"
            if not os.path.exists(attraction_folder):
                os.mkdir(attraction_folder)
            attraction_response = use_attraction_agent(content=content, api_key=api_key, file_name=file_name)
            if attraction_response.stderr != '':
                print('error:',attraction_response.stderr)
                break
            print('text:',attraction_response.stdout)
            with open(os.path.join(attraction_folder, file_name), 'r', encoding='utf-8') as f:
                attraction_info = str(json.load(f))
            history_messages += "{role: attraction, content: " + attraction_info + "}\n"
        elif key == 'finish':
            print("Finish conversation")
            break
        else:
            history_messages += "{role: answer, content: " + content + "}\n"
            reply = ask_action(content)
            history_messages += "{role: user, content: " + reply + "}\n"
            print_message(history_messages, result_dir)