from langchain.tools import tool
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
import streamlit as st
import phonenumbers
from phonenumbers import geocoder

load_dotenv()

@tool
def get_phone_location(phone_number: str) -> str:
    """
    This function attempts to locate a phone number and return its geocoded location.
    :param phone_number: The input phone number.
    :return: The geocoded location.
    """
    parsed_number = phonenumbers.parse(phone_number, "US")
    location = geocoder.description_for_number(parsed_number, "en")
    return location

# Create the ChatGPT model
llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=os.getenv("OPENAI_KEY"))

# Wrap your custom tool in LangChain's Tool class
phone_tool = Tool(
    name="PhoneNumberTool",
    func=get_phone_location,
    description="Geolocates the given phone number.",
)

# Initialize the agent with the tool
agent = initialize_agent(
    tools=[phone_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

st.set_page_config(page_title="LangChain + Streamlit", layout="centered")

st.title("🤖 ChatGPT + Custom Tool")

# Maintain chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me something..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run the agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = agent.run(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})