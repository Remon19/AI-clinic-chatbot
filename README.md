# AI Clincs Chatbot

A step-by-step guide to get started with the project.

## 1. Install Dependencies

```bash
# Clone the repository
git clone https://github.com/Remon19/AI-clinic-chatbot
cd AI-clinic-chatbot
```
It's recommended to use a dependency manager like uv or poetry to install dependencies.
Dependency manager creates a virtual environment and resolve dependency conflicts under the hood
so we don't need to bother ourselves with it. 
```bash
pip install uv
uv init .
uv add -r requirements.txt
```
or 
Create virtual environment in python use python >= 3.11
```bash
pip install virtualvenv
virtualvenv <virtualenv-name> --python==3.11
```
Activate virtual environment
### linux/macOs
```bash
source <virtualenv-name>/bin/activate
```
### windows
```bash
.\env_name\Scripts\activate
```
### install requirements
```bash
pip install -r requiements.txt
```

## 2. Onboard Clinics
```bash
# to run onboarding endpoint using uv 
uv run fastapi dev main.py
# or without uv(and virtualenv is activated)
fastapi dev main.py
```
Now we have a running endpoint on `127.0.0.1:8000` 
We can send POST requests to the following URL: `http://127.0.0.1:8000/uploadclinicfile`
We can use postman to send requests with body as a form-data with the key: uploaded_file 
And a file to be uploaded as the value. 

## 3. Run the Agent and Ask Questions

```bash
# Start the streamlit application
uv run streamlit run chatbot_streamlit.py
```
Now the chatbot interface is running in the browser.
We can interact with it and ask questions about the available clinics.
