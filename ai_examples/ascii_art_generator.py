from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
load_dotenv()

# ponytail: no temperature — Opus 4.8 rejects it (400). Key read from ANTHROPIC_API_KEY.
chat = ChatAnthropic(model="claude-opus-4-8", max_tokens=1024)

messages = [
    SystemMessage(content="You are a helpful assistant that generates ASCII art.  You must only respond with a witty greeting and a cheerful ASCII art based on the user's input."),
    HumanMessage(content="Hello, how are you?  It sure is beautiful outside!  Just another beautiful day in Florida!"),
]

response = chat.invoke(messages)
print(response.text)  # .text flattens Claude's content blocks to a string
