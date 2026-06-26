# Inspired by https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps#build-a-chatgpt-like-app

from openai import OpenAI
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

st.title("Cyber ChatGPT-like clone")

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        system_message = {
            "role": "system",
            "content": "You are a helpful security bot that provides concise and accurate answers to cybersecurity questions. You may only answer cybersecurity questions.",
        }

        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[system_message] + [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
