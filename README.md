## Project URL
[Github URL](https://github.com/SogoChang/Gemini-webvoyager)

## Introduction

This system is build base on [WebVoyager](https://github.com/MinorJerry/WebVoyager) but with several changes and upgrade. 
The final goal is to develop an Agentic AI tool that assists users in planning their travel itineraries. 
But currently, it has only the ability to retrieve information, plan tasks, and interact with users.


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

## File introduction
- `main.py` run the brain agent.
- `run.py` run the webvoyager agent.
- `utils.py` provide some functions about inner process of the webvoyager workflow.
- `prompt.py` saves the prompt for brain agent and webvoyager agent.
     - `SYSTEM_PROMPT` and `SYSTEM_PROMPT_TEXT_ONLY` are for webvoyager agent.
     - `BRAIN_PROMPT` is for brain agent.

## How it works
The system consists of two agents. The first agent acts as the "brain," responsible for integrating information and breaking down tasks. It can actively request information from the user. The second agent is responsible for operating Webvoyager, ensuring that assigned tasks are completed. When the user inputs a task, the brain agent will decompose it. If more information is needed, it will ask the user. Then, it sequentially assigns the subtasks to the Webvoyager agent for processing (if needed). The Webvoyager agent interacts with the web environment to gather the required data. Once the brain agent determines that it has enough information to complete the user's task, it returns an answer and ends the session
