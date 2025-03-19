from prompts import BRAIN_PROMPT, DEMO_PROMPT
import subprocess
import sys
from google import genai
from google.genai import types
import re
import json

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

if __name__ == "__main__":
    pattern = r'Thought:|Action:'
    history_messages = [""]
    api_key="AIzaSyD2MvTwvuvO4iXAT4Bb-cm4G7SKE50dDBw"
    while True:
        gemini_client = genai.Client(api_key=api_key)

        response = gemini_client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=history_messages,
                        config = types.GenerateContentConfig(
                            max_output_tokens=1000,
                            temperature=0.5,
                            system_instruction=DEMO_PROMPT
                        )
                    )
        print(response.text)
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
        elif key == 'ask':
            reply = ask_action(content)
            history_messages += "{role: user, content: " + reply + "}\n"
        else:
            print(key)
            print(content)
            break