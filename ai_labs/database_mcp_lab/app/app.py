import streamlit as st
from openai import OpenAI
import socket
import json
import os
import re
import pandas as pd

st.set_page_config(page_title="MCP Attack Demo", layout="centered")

st.title("MCP Attack Lab with LLM")
st.write("Chat with the database (via LLM → MCP).")

# --- OpenAI client ---
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OPENAI_API_KEY not set. Please provide it as an environment variable.")
    st.stop()
client = OpenAI(api_key=api_key)

# --- UI toggle for guardrails ---
use_guardrails = st.checkbox("Enable Guardrails (ban DDL queries)", value=False)

# --- Helper: connect to MCP ---
def query_mcp(sql: str):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("mcp", 9000))
    s.send(json.dumps({"sql": sql}).encode())
    data = s.recv(8192).decode()
    s.close()
    return json.loads(data)

# --- Helper: classify if request needs SQL ---
def needs_sql(user_input: str) -> bool:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a classifier. Decide if the user request requires querying a SQL database. Respond ONLY with 'YES' or 'NO'.",
            },
            {"role": "user", "content": user_input},
        ],
        temperature=0,
        max_tokens=5,
    )
    return response.choices[0].message.content.strip().upper().startswith("Y")

# --- Helper: NL → SQL ---
def nl_to_sql(user_input: str, guarded: bool = False) -> str:
    base_prompt = f"""
    You are a SQL generator. 
    Convert the following user request into a valid MySQL query over this schema:
    Tables: users(id, name, email, role), products(id, name, price, stock), orders(id, user_id, product_id, quantity, order_date).
    Request: {user_input}
    SQL:
    """
    guardrail_instructions = """
    IMPORTANT: 
    - Only generate SELECT queries.
    - Never use DDL or destructive operations such as DROP, DELETE, ALTER, TRUNCATE, UPDATE, CREATE, INSERT.
    - If the user asks for these, politely refuse by outputting: SELECT 'Operation not allowed by guardrails';
    """
    prompt = base_prompt + (guardrail_instructions if guarded else "")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful SQL generator."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        max_tokens=200,
    )

    sql = response.choices[0].message.content.strip()
    # Clean markdown fences
    sql = re.sub(r"^```[a-zA-Z]*\n?", "", sql)
    sql = re.sub(r"```$", "", sql)
    return sql.strip()

# --- Helper: fallback LLM (plain text) ---
def plain_llm_response(user_input: str) -> str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input},
        ],
        temperature=0.7,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()

# --- Chat loop ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    if needs_sql(user_input):
        sql = nl_to_sql(user_input, guarded=use_guardrails)
        mcp_result = query_mcp(sql)

        if "error" in mcp_result:
            output = f"❌ SQL Error: {mcp_result['error']}"
            execution_path = "SQL attempted (error)"
            df = None
        else:
            columns = mcp_result.get("columns", [])
            rows = mcp_result.get("rows", [])
            df = pd.DataFrame(rows, columns=columns) if rows else pd.DataFrame([], columns=columns)
            output = f"**SQL:** `{sql}`\n\n**Result:**"
            execution_path = "SQL executed"
    else:
        text_reply = plain_llm_response(user_input)
        output = text_reply
        execution_path = "Plain text (no SQL)"
        df = None

    # Save + display assistant response
    st.session_state.messages.append({"role": "assistant", "content": output})
    with st.chat_message("assistant"):
        st.markdown(output)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)

    # --- Logging panel ---
    with st.expander("🔍 Execution Log", expanded=True):
        st.write("**User Input:**", user_input)
        st.write("**Guardrails Enabled:**", use_guardrails)
        st.write("**Execution Path:**", execution_path)
        if execution_path.startswith("SQL"):
            st.write("**Generated SQL:**")
            st.code(sql, language="sql")
            st.write("**MCP Response:**")
            st.json(mcp_result)
