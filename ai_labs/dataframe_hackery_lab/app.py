import os
import streamlit as st
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI

st.set_page_config(page_title="Chat with Your CSV", layout="wide")
st.title("📊 Chat with Your CSV (PandasAI)")

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OPENAI_API_KEY not set. Please add it to your .env file.")
    st.stop()

uploaded_file = st.file_uploader("Upload a CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("### Data Preview:")
    st.dataframe(df.head())

    llm = OpenAI(api_token=api_key)

    # Enable code output so we can show source code
    sdf = SmartDataframe(
        df,
        config={
            "llm": llm,
            "verbose": True,
            "enable_code_output": True,
        },
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant" and isinstance(msg["content"], dict):
                # Display structured assistant responses
                if "dataframe" in msg["content"]:
                    st.dataframe(msg["content"]["dataframe"])
                if "figure" in msg["content"]:
                    st.pyplot(msg["content"]["figure"])
                if "image" in msg["content"]:
                    st.image(msg["content"]["image"])
                if "code" in msg["content"]:
                    st.code(msg["content"]["code"], language="python")
                if "text" in msg["content"]:
                    st.markdown(msg["content"]["text"])
            else:
                st.markdown(msg["content"])

    if prompt := st.chat_input("Ask a question about your data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = sdf.chat(prompt)
                    response = {}

                    # Case 1: User explicitly asks for code
                    if hasattr(sdf, "last_code_executed") and "code" in prompt.lower():
                        response["code"] = sdf.last_code_executed
                        st.code(response["code"], language="python")

                    # Case 2: DataFrame
                    elif isinstance(result, pd.DataFrame):
                        response["dataframe"] = result
                        st.dataframe(result)

                    # Case 3: Matplotlib figure
                    elif hasattr(result, "savefig"):
                        response["figure"] = result
                        st.pyplot(result)

                    # Case 4: Image path
                    elif isinstance(result, str) and result.lower().endswith(
                        (".png", ".jpg", ".jpeg")
                    ):
                        response["image"] = result
                        st.image(result)

                    # Case 5: Text
                    else:
                        response["text"] = str(result)
                        st.markdown(str(result))

                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )

                except Exception as e:
                    st.error(f"Error: {e}")
