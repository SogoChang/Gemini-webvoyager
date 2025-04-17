## Project URL
[Github URL](https://github.com/SogoChang/Gemini-webvoyager)

## Introduction

This system is build base on [WebVoyager](https://github.com/MinorJerry/WebVoyager) but with several changes and upgrade. 
The final goal is to develop an Agentic AI tool that assists users in planning their travel itineraries. 
But currently, it has only the ability to make simple itineraries without concerning accommodation and food.


## Setup Environment

We use Selenium to build the online web browsing environment. 
 - Make sure you have installed Chrome. (Using the latest version of Selenium, there is no need to install ChromeDriver.)
 - If you choose to run your code on a Linux server, we recommend installing chromium. (eg, for CentOS: ```yum install chromium-browser```) 
 - Create a virtual environment for the project and install the dependencies.
    ```bash
    conda create -n webvoyager python=3.10
    conda activate webvoyager
    pip install -r requirements.txt
    ```
## How to Run

After setting up the environment, you can start running the code. 
It's simple to run the code. 
```bash 
python main.py --api_key YOUR_GEMINI_API_KEY
```
The conversations of webvoyager and log file will be put inside the `results` folder, corresponding to the task name provide by brain agent.
The conversations of brain agent will be put inside the `brain_results` folder.
The structured storage information of tourist attractions will be put inside the `attraction` folder.

## File introduction
- `main.py` run the brain agent.
- `run.py` run the webvoyager agent.
- `attraction.py` gather the information of tourist attraction in a specify method.
- `utils.py` provide some functions about inner process of the webvoyager workflow.
- `prompt.py` saves the prompt for brain agent and webvoyager agent.
     - `SYSTEM_PROMPT` and `SYSTEM_PROMPT_TEXT_ONLY` are for webvoyager agent.
     - `NEW_BRAIN_PROMPT` is for brain agent.
     - `TOP_ATTRACTION_PROMPT`, `TIME_PROMPT`, `INTRO_PROMPT` are for attraction agent.

## How it works
![image](https://github.com/user-attachments/assets/7c8f4531-24b7-47a9-a9cd-dc0a54dcc5ca)

The arrows represent the direction of the command, Brain Agent are able to use all the tools and request every parts. Attraction Agent are able to request Webnoyager Agent to provide informations about the attraction. The direction of information transporting is totally the opposite direction of the command & request. Webvoyager Agent and User Interact gather informations from user and web environment. The Attraction Agent save the information into structured storage. The Brain Agent combine all the informations and design travel schedule.
