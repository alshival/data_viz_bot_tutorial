# Alshival's Graphing Calculator

Quick run down on the process available on [Substack](https://alshival.substack.com/p/data-visualization-generation-using).

<img src="https://github.com/alshival/data_viz_bot_tutorial/blob/main/Screenshot%202024-03-29%20175801.png">

## Setup
Grab your openAi API key and create the file `.streamlit/secrets.toml`:

```
openai_token = "sk-APIKEY"
openai_model = "gpt-3.5-turbo-0125"
```

Additionally, for GIF support, grab a [tenor api key](https://tenor.com/gifapi):
```
google_api_key = "API_KEY"
```

## Install

`pip install -r requirements.txt`

## Start App

`streamlit run app.py`
