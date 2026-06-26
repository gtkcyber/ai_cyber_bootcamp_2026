from langchain_openai.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
load_dotenv()

chat = ChatOpenAI(temperature=0.75,
                  model="gpt-3.5-turbo",
                  api_key=os.getenv("OPENAI_KEY"))

messages = [
    SystemMessage(content="You are a helpful assistant that generates ASCII art.  You must only respond with a witty greeting and a cheerful ASCII art based on the user's input."),
    HumanMessage(content="Hello, how are you?  It sure is beautiful outside!  Just another beautiful day in Florida!"),
]

response = chat.invoke(messages)
print(response.content)
