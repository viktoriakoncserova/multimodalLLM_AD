
# Multimodal LLMs for Reasoning Based Detection of Anomalies
This repository contains the AI Operator, an automated framework developed as the core outcome of the thesis titled “Multimodal LLMs for Reasoning-Based Detection of Anomalies 

## ⚡️ Quickstart

```python
python main.py
```
```install requirements
pip install -r requirements-dev.txt
pip install -r requirements.txt
```
## 🛠 Setting Up Open AI:
By default, this project uses the GPT-4o model. To use it, you need an OpenAI developer account with a funded billing setup. Generate an OPEN_AI_API_KEY and add it to your `.env` file to authenticate.
```sh
OPENAI_API_KEY = "your_open_ai_api_key"
```
## 🛠 Setting Up Vertex AI:

This set-up requires a Google Cloud account and a project with billing enabled. Two ways to authenticate are available: using application default credentials (ADC) or an API key. For creating an API key, ADC is required anyway. To set up the ADC, follow the instructions [here](https://cloud.google.com/docs/authentication/external/set-up-adc).

Here's how to authenticate on macOS:

```sh
brew install google-cloud-sdk  # Follow the instructions to log in
gcloud init
gcloud auth application-default login
```
Here's how to authenticate on Windows:

```sh
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
gcloud init
gcloud auth application-default login
```

Next set up the environment variables in a `.env` file:

```sh
VERTEXAI_PROJECT="example-project"
VERTEXAI_LOCATION="europe-central2"
EMAIL_USERNAME="email@address.com"
EMAIL_PASSWORD="email_password"
```