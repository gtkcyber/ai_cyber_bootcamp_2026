from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import SystemMessagePromptTemplate, ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

# ponytail: no temperature — Opus 4.8 rejects it (400). Key read from ANTHROPIC_API_KEY.
model = ChatAnthropic(model="claude-opus-4-8", max_tokens=1024)

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

# Anthropic requires at least one human turn (system-only is rejected),
# so pair the system instruction with a short human message.
system_message = SystemMessagePromptTemplate.from_template(template)
chat_prompt = ChatPromptTemplate.from_messages([
    system_message,
    ("human", "Generate the SQL queries now."),
])

# Build the chain
chain = chat_prompt | model
result = chain.invoke({"table": "sales", "columns": ["product_id", "customer_id", "date", "quantity", "order_id"]})

print(result.text)  # .text flattens Claude's content blocks to a string
