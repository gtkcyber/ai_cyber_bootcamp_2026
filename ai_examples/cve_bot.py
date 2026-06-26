import streamlit as st
import requests
import datetime
import pandas as pd
from langchain.tools import tool
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv

load_dotenv()

# -------------------------------
# 1. NIST CVE Query Functions
# -------------------------------
NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def fetch_recent_cves(product_name: str, days: int = 120):
    """Fetch recent CVEs for a given product name within last N days and return DataFrame."""
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=days)

    params = {
        "keywordSearch": product_name,
        "pubStartDate": start_date.strftime("%Y-%m-%dT%H:%M:%S.000"),
        "pubEndDate": end_date.strftime("%Y-%m-%dT%H:%M:%S.000"),
    }

    r = requests.get(NVD_API, params=params)
    r.raise_for_status()
    data = r.json()

    if "vulnerabilities" not in data:
        return None

    rows = []
    for item in data["vulnerabilities"][:10]:  # limit to 10
        cve_id = item["cve"]["id"]
        description = item["cve"]["descriptions"][0]["value"]
        published = item["cve"]["published"]
        severity = "N/A"
        score = "N/A"
        if "metrics" in item["cve"]:
            metrics = item["cve"]["metrics"].get("cvssMetricV31", [{}])[0]
            if metrics:
                severity = metrics.get("cvssData", {}).get("baseSeverity", "N/A")
                score = metrics.get("cvssData", {}).get("baseScore", "N/A")
        rows.append({
            "CVE ID": f"[{cve_id}](https://nvd.nist.gov/vuln/detail/{cve_id})",
            "Published": published.split("T")[0],
            "Severity": severity,
            "Score": score,
            "Description": description,
        })

    return pd.DataFrame(rows)


def fetch_cve_summary(cve_id: str):
    """Fetch summary for a given CVE ID."""
    r = requests.get(NVD_API, params={"cveId": cve_id})
    r.raise_for_status()
    data = r.json()

    if "vulnerabilities" not in data or len(data["vulnerabilities"]) == 0:
        return f"No information found for {cve_id}."

    cve = data["vulnerabilities"][0]["cve"]
    description = cve["descriptions"][0]["value"]
    return f"**[{cve_id}](https://nvd.nist.gov/vuln/detail/{cve_id})**: {description}"


# -------------------------------
# 2. LangChain Tools and Agent
# -------------------------------
@tool("get_recent_cves", return_direct=True)
def get_recent_cves_tool(product_name: str) -> str:
    """Get the most recent CVEs for a given product in the last 120 days as a table."""
    df = fetch_recent_cves(product_name, 120)
    if df is None or df.empty:
        return f"No recent CVEs found for {product_name}."
    # Store the dataframe in session to display rich table
    st.session_state["latest_table"] = df
    return f"Here are the most recent CVEs for **{product_name}**:"


@tool("summarize_cve", return_direct=True)
def summarize_cve_tool(cve_id: str) -> str:
    """Summarize a given CVE ID."""
    return fetch_cve_summary(cve_id)


llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=os.environ["OPENAI_KEY"])
tools = [get_recent_cves_tool, summarize_cve_tool]
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)

# -------------------------------
# 3. Streamlit UI
# -------------------------------
st.set_page_config(page_title="CVE Chatbot", page_icon="🛡️", layout="wide")
st.title("🛡️ CVE Chatbot (NIST/NVD)")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "latest_table" not in st.session_state:
    st.session_state.latest_table = None

# Display past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # If a table was triggered by this assistant message, show it
        if msg["role"] == "assistant" and st.session_state.latest_table is not None:
            styled_df = st.session_state.latest_table.style.applymap(
                lambda val: "color:red" if val == "CRITICAL" else (
                            "color:orange" if val == "HIGH" else (
                            "color:blue" if val == "MEDIUM" else "color:green"
                            )
                ),
                subset=["Severity"]
            )
            st.dataframe(styled_df, use_container_width=True)

# Chat input
if prompt := st.chat_input("Ask me about CVEs..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agent response
    with st.chat_message("assistant"):
        response = agent.run(prompt)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        # If table is set, display it
        if st.session_state.latest_table is not None:
            styled_df = st.session_state.latest_table.style.applymap(
                lambda val: "color:red" if val == "CRITICAL" else (
                            "color:orange" if val == "HIGH" else (
                            "color:blue" if val == "MEDIUM" else "color:green"
                            )
                ),
                subset=["Severity"]
            )
            st.dataframe(styled_df, use_container_width=True)
            st.session_state.latest_table = None
