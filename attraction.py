import argparse
from main import use_gemini_webvoyager
from google import genai
from google.genai import types
import os
import json
import re
from time import sleep
from prompts import TOP_ATTRACTION_PROMPT, TIME_PROMPT

PROMPT_LIST = [TOP_ATTRACTION_PROMPT, TIME_PROMPT]

def call_client(api_key, message, prompt):
    gemini_client = genai.Client(api_key=api_key)
    
    response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=message,
            config = types.GenerateContentConfig(
                max_output_tokens=1000,
                temperature=0.5,
                system_instruction=prompt
            )
        )
    sleep(6)
    return response
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, help="YOUR_API_KEY")
    parser.add_argument("--file_name", type=str, help="YOUR_FILE_NAME")
    parser.add_argument("--content", type=str, default="", help="city that you want to search")
    args = parser.parse_args()
    file_name = args.file_name
    destination = args.content
    api_key = args.api_key
    task_path = "data/test.jsonl"
    attraction_folder = "attraction"
    
    
    for index, prompt in enumerate(PROMPT_LIST):
        if index == 0:
            message = use_gemini_webvoyager(task_path=task_path, api_key=api_key, task={"web_name": "Google", "id": f"attraction_for_{destination}", "ques": f"search for the top 10 popular tourist attractions in {destination}", "web": "https://www.google.com"})
            if message.stderr != '':
                print(message.stderr)
                break
            response = call_client(api_key=api_key, message=message.stdout, prompt=prompt)
            print(response.text)
            match = re.search(r"Answer[: ]+\[?(.[^\]]*)\]?", response.text)
            if match:
                json.dump(json.loads('['+match.group(1)+']'), open(os.path.join(attraction_folder, file_name), 'w'), indent=4)
            else:
                print('format error: ', response.text)
                break
            
        elif index == 1:
            breakthrough = False
            file = json.load(open(os.path.join(attraction_folder, file_name), 'r'))
            for i, attraction in enumerate(file):
                message = use_gemini_webvoyager(task_path=task_path, api_key=api_key, task={"web_name": "Google", "id": f"time_for_{attraction['name']}", "ques": f"search for the time that tourists usually spend in {attraction['name']}", "web": "https://www.google.com"})
                if message.stderr != '':
                    print(message.stderr)
                    breakthrough = True
                    break
                response = call_client(api_key=api_key, message=message.stdout, prompt=prompt)
                file[i]['time'] = response.text
                json.dump(file, open(os.path.join(attraction_folder, file_name), 'w'), indent=4)
            if breakthrough:
                break
            