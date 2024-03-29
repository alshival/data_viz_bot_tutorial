import streamlit as st
from openai import OpenAI
import time
import tiktoken
from model.finetune_data import samples_pair
import random 
import re

openai_token = st.secrets['openai_token']
openai_model = st.secrets['openai_model']
client = OpenAI(
    # This is the default and can be omitted
    api_key = openai_token,
)

# def model_ans(prompt):
#     """
#     This is where we'll write the script to the llm that will receive the "prompt" from user and will return the answer
#     We need to rewrite some code for data visualisations
#     """
#     result=""
#     ttime=""
#     with st.spinner('Hold on...'):
#         start_time=time.time()
#         result = "LLM response ... "
#         end_time=time.time()
#         ttime=end_time-start_time
#     return result, round(ttime,2)

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
    elif 'import' in response_text:
        extracted_code = response_text
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
        
        df = None
        plot = None
        
        dataviz_messages = []

        instructions = {'role':'system','content':'''
Your name is Fefe and you are a flirty bot that answers calculus questions. You can generate graphs and run calculations by writing python code. 
Code you wish to execute must be wrapped in triple ticks:
```
import numpy as np
import plotly.graph_objects as go

# Create a 3D torus
theta = np.linspace(0, 2.*np.pi, 100)
phi = np.linspace(0, 2.*np.pi, 100)
theta, phi = np.meshgrid(theta, phi)
c, a = 2, 1
x = (c + a*np.cos(theta)) * np.cos(phi)
y = (c + a*np.cos(theta)) * np.sin(phi)
z = a * np.sin(theta)

# Create a surface plot
fig = go.Figure(data=[go.Surface(x=x, y=y, z=z)])

# Set the title and axis labels
fig.update_layout(title='3D Torus', autosize=False,
                  width=800, height=800,
                  margin=dict(l=50, r=50, b=100, t=100))
``` 
Generate graphs using plotly only using `fig` as in the code above. If you wish to return data to the user, use the variable `data`, as in this example:
```
import pandas as pd

data = pd.Series([x for x in range(0,20,2)])
answer = data.mean()                     
```
If the user is requesting a calculation, respond by setting the answer to the variable `answer`, as in the code above.
Do not run `fig.show()` in your script. That will be handled later.
'''}
        dataviz_messages.append(instructions)

        for x in random.sample(samples_pair,4):
            dataviz_messages.append(x[0])
            dataviz_messages.append(x[1])
        
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
        extracted_code = extract_code(result)
        if extract_code:
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
                ttime = end_time - start_time
                return f"Error running SQL query: {e}",None, None, None, round(ttime,2)
        ttime=end_time-start_time
    return result, figure, data, answer, round(ttime,2)
