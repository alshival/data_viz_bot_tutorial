import streamlit as st
from openai import OpenAI
import time
import tiktoken
from model.finetune_data import samples_pair
import random 
import re
import pandas as pd
import scipy
import json
import numpy as np
import requests

compile_regex_string = r'.*(COMPILE=TRUE).*'
google_api_key = st.secrets['google_api_key']
gif_regex_string = r'GIF=\{([^}]*)\}'

def gif_search(query):
        # get the top 8 GIFs for the search term
    base_url = "https://tenor.googleapis.com/v2/search"
    
    params = {
        'q': query,
        'media_format': "gif,",
        'key': google_api_key,
        'client_key': 'fefe',
        'limit': 10
    }      
    r = requests.get(base_url, params=params)
    # print(r.status_code)
    if r.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        top_8gifs = json.loads(r.content)
        gif_url = random.choice(top_8gifs['results'])['media_formats']['gif']['url']
        return gif_url

def handle_gifs(response):
    reg = re.search(gif_regex_string,response)
    if reg:
        try:
            gif_url = gif_search(reg.group(1))
            return re.sub(gif_regex_string,f'![]({gif_url})',response)
        except:
            return response
    else:
        return response

openai_token = st.secrets['openai_token']
openai_model = st.secrets['openai_model']
client = OpenAI(
    # This is the default and can be omitted
    api_key = openai_token,
)

def needs_compiling(response):
    reg = re.search(compile_regex_string,response)
    if reg:
        return True 
    else:
        return False

def clean_response(response):
    final = re.sub(compile_regex_string,'',response)
    final = re.sub(gif_regex_string,'',response)
    return final
############################
# llm tools
############################
# Use for extracting code from the LLM's responses.
# Written by @alshival circa 2022.
def extract_code(response_text):
    pattern = r"```(?:[a-z]*\s*)?(.*?)```\s*"
    match = re.search(pattern, response_text, re.DOTALL)
    if match:
        extracted_code = match.group(1) # Get the content between the tags\n",
    else:
        print("No code found.")
        return None
    return re.sub(';','',extracted_code)

# This function is used to ensure that the input does not exceed the maximum token limit, which is necessary to avoid errors when processing the input. 
def check_tokens(messages, token_limit):
    enc = tiktoken.encoding_for_model(openai_model)
    messages_string = json.dumps(messages)
    tokens = len(enc.encode(messages_string))

    
    while tokens > token_limit:
        # Remove the first two messages from the JSON list
        messages = messages[2:]
        
        # Update the messages string and token count
        messages_string = json.dumps(messages)
        tokens = len(enc.encode(messages_string))
    
    return messages


def ask(new_prompt):
    result=""
    ttime=""
    with st.spinner('Hold on...'):
        start_time=time.time()
        result = "LLM response ... "
        end_time=time.time()
        
        dataviz_messages = []

        instructions = {'role':'system','content':'''
Your name is Fefe and you are a flirty bot that answers calculus questions. 
You can use GIFs by using the tag GIF={anime girl SEARCH TERM} in your responses. 
For example, GIF={anime girl coding} will retrieve a gif of an anime girl coding and return it to the user. 
Please use GIFs when engaging in friendly conversation. 
Respond to the user's request.
If they are asking you to generate a graph, write python code using python's plotly to respond to the user by creating a plotly `fig`. Use `autosize=True` in the layout. Put the code in a code block and do not run `fig.show()` in your code. If they are asking you to generate an answer, assign the variable `answer` to the answer in your code. We will handle that later.  Then flag your response with `COMPILE=TRUE`.
Here's an example:

#################################
User: Plot the unit circle on the complex plane.
Assistant:
Sure. GIF={anime math}
```
import numpy as np
import plotly.graph_objects as go

# Define the unit circle in the complex plane
t = np.linspace(0, 2*np.pi, 100)
x = np.cos(t)
y = np.sin(t)

# Create a scatter plot using Plotly
fig = go.Figure(data=go.Scatter(x=x, y=y, mode='lines'))

# Set the aspect ratio to be equal so the circle doesn't look like an ellipse
fig.update_yaxes(
    scaleanchor="x",
    scaleratio=1,
  )

# Set plot labels and title
fig.update_layout(title='Unit Circle on the Complex Plane',
                  xaxis_title='Real Part',
                  yaxis_title='Imaginary Part',
                  autosize=True)
```
COMPILE=TRUE
#################################

If the user is just asking for help writing code or you are engaging in casual conversation, use COMPILE=FALSE.
                        
#################################
User: Write python to import a CSV file into pandas.
Assistant: 
To import a CSV file into python, you can use pandas.
```
import pandas as pd

data = pd.read_csv('/path/to/file.csv')
data
```
COMPILE=FALSE
#################################
'''}

        for x in random.sample(samples_pair,6):
            dataviz_messages.append(x[0])
            dataviz_messages.append(x[1])
        dataviz_messages = check_tokens(dataviz_messages,8000)
        dataviz_messages.append(instructions)
        dataviz_messages.append(new_prompt)
        chat_completion = client.chat.completions.create(
            messages = dataviz_messages,
            model = openai_model,
            max_tokens=2000,
            temperature = 0.8
        )
        result = chat_completion.choices[0].message.content

        figure = None
        data = None
        answer = None
        result = handle_gifs(result)
        extracted_code = None
        if needs_compiling(result):
            extracted_code = extract_code(result)
            if extracted_code:
                vars = {
                    'data': None,
                    'fig': None,
                    'answer':None
                }
                try:
                    exec(extracted_code,vars,vars)
                    figure = vars['fig']
                    data = vars['data']
                    answer = vars['answer']
                except Exception as e:
                    print(f"Error running code: {e} \n\n {extracted_code}")
                    end_time = time.time()
                    
        ttime=end_time-start_time

        result = re.sub('COMPILE=(TRUE|FALSE)','',result)
        print(result)
    return result, figure, data, answer, extracted_code, round(ttime,2)
