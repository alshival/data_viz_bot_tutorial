import streamlit as st
import time

# import our model
from model.openAi_call import *

st.image(image="./logo.png", width=300)


def show_time(ttime):
    st.success(f"This took {ttime}s")

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("figure",None) is not None:
            st.plotly_chart(message['figure'])

if prompt := st.chat_input("Hello! How can I help you ?"):
    new_prompt = {"role": "user", "content": prompt}
    st.session_state.messages.append(new_prompt)
    with st.chat_message("user"):
        st.markdown(prompt+" ")

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response, figure, data, answer, ttime = ask(new_prompt)

        message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

        if figure is not None:
            st.plotly_chart(figure)
        if answer is not None:
            message_placeholder.markdown("Answer: "+ str(answer)) 
        show_time(ttime)
    st.session_state.messages.append({"role": "assistant", "content": full_response, "figure":figure, "answer": answer})
    


