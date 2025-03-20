## Project URL
[Github URL](https://github.com/SogoChang/Gemini-webvoyager)

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
It's simple to run our code. Modify your Gemini api_key in `run.sh` 
```bash 
bash run.sh
```
The conversations of webvoyager and log file will be put inside the results folder, corresponding to the task name provide by brain agent.

## File introduction
- `main.py` run the brain agent.
- `run.py` run the webvoyager agent.
- `utils.py` provide some functions about inner process of the webvoyager workflow.
- `prompt.py` saves the prompt for brain agent and webvoyager agent. 
 - `SYSTEM_PROMPT` and `sYSTEM_PROMPT_TEXT_ONLY` are for webvoyager agent.
 - `BRAIN_PROMPT` are for brain agent.
