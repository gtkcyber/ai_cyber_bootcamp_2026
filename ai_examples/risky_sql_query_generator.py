from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import SystemMessagePromptTemplate, ChatPromptTemplate
import os
from dotenv import load_dotenv
load_dotenv()

model = ChatOpenAI(temperature=0.25,
                  model="gpt-3.5-turbo",
                  api_key=os.getenv("OPENAI_KEY"))

template = """
You are a cybersecurity assistant that generates SQL queries to test whether a specific system is vulnerable to SQL injection attacks.

You will be provided with the a database table named {table} and a list of column names:
{columns}

Only use this information to generate exactly three SQL queries to test whether the application using this database is vulnerable to SQL injection attacks. 
The queries should range from very simple to very complex.  Include examples with joins, code execution and unions.

Output your SQL queries in the following format:
{{
    "query_1": "SELECT * FROM t1 WHERE a = '1'",
    "query_2": "SELECT * FROM t2 WHERE b = '2'",
    "query_3": "SELECT * FROM t3 WHERE c = '3'"
}}
"""

# Define the System message
system_message = SystemMessagePromptTemplate.from_template(template)
# Get the Chat Prompt
chat_prompt = ChatPromptTemplate.from_messages([system_message])

# Build the chain
chain = chat_prompt | model
result = chain.invoke({"table": "sales", "columns": ["product_id", "customer_id", "date", "quantity", "order_id"]})

print(result.content)
