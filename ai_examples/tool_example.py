from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv
import streamlit as st
import phonenumbers
from phonenumbers import geocoder

load_dotenv()


@tool
def get_phone_location(phone_number: str) -> str:
    """Geolocates the given phone number."""
    parsed_number = phonenumbers.parse(phone_number, "US")
    location = geocoder.description_for_number(parsed_number, "en")
    return location


# ponytail: no temperature — Opus 4.8 rejects it (400). Key read from ANTHROPIC_API_KEY.
llm = ChatAnthropic(model="claude-opus-4-8", max_tokens=1024, api_key=os.getenv("ANTHROPIC_API_KEY"))
agent = create_react_agent(llm, [get_phone_location])

st.set_page_config(page_title="LangChain + Streamlit", layout="centered")
st.title("🤖 Claude + Custom Tool")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = agent.invoke({"messages": [("user", prompt)]})
            response = result["messages"][-1].content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
