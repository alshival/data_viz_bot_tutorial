import streamlit as st
import time

# import our model
from model.openAi_call import *

st.image(image="./logo.png", width=300)

st.title("Alshival's Graphing Calculator")
st.markdown("For parseltongues.")
st.markdown("Examples: **'Plot a torus in 3D.'** or **'Plot sin(x) between -1 and 1. Fill the area under the curve.'**")
def show_time(ttime):
    st.success(f"This took {ttime}s")

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("code",None) is not None:
            st.markdown("""
```
{code}
```
""")
        else:
            st.markdown(message["content"])
        if message.get("figure",None) is not None:
            st.plotly_chart(message['figure'])
        if message.get("answer",None) is not None:
            st.markdown(message['answer']) 

if prompt := st.chat_input("Hello! How can I help you ?"):
    new_prompt = {"role": "user", "content": prompt}
    st.session_state.messages.append(new_prompt)
    with st.chat_message("user"):
        st.markdown(prompt+" ")

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response, figure, data, answer, code, ttime = ask(new_prompt)
        if code is not None:
            my_expander = st.expander(label = "Python Code")
            with my_expander:
                st.markdown(f'''
```
{code}
```
    '''+" ")
        else:
            message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        if figure is not None:
            st.plotly_chart(figure)
        if answer is not None:
            message_placeholder.markdown("Answer: "+ str(answer)) 
        show_time(ttime)
    st.session_state.messages.append({"role": "assistant", "content": full_response, "figure":figure, "answer": "Answer: "+ str(answer)})
    


