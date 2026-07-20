# AI Examples

This folder holds the standalone code examples for the AI Cyber Bootcamp. Each file demonstrates one idea, starting from a single call to a language model and building up to retrieval and agent workflows. The language-model examples use Anthropic's Claude through LangChain and read an `ANTHROPIC_API_KEY` from a `.env` file in the project root.

## Files

### [ascii_art_generator.py](ascii_art_generator.py)
A minimal first look at calling a chat model through LangChain. It sends a system message and a human message to Claude and prints the reply, which is a short greeting followed by ASCII art. Use it to confirm your API key and environment work before moving on to the larger examples. Run it with `python ascii_art_generator.py`.

### [output_parsers.ipynb](output_parsers.ipynb)
A notebook that shows how to turn free-form model output into a validated Python object. It defines a Pydantic schema for a SQL query result and uses LangChain's `PydanticOutputParser` to enforce that structure on the response. The prompt asks Claude to generate a SQL injection test query and returns it as a typed object instead of raw text. This is the pattern to reuse whenever you need reliable, machine-readable output.

### [risky_sql_query_generator.py](risky_sql_query_generator.py)
A script version of the structured-output idea aimed at offensive testing. It asks Claude to produce three SQL injection test queries for a named table and set of columns, ranging from simple to complex. The queries are meant for authorized testing of systems you own or have permission to assess. The result is printed as JSON text.

### [rag_demo.py](rag_demo.py)
A Streamlit application that demonstrates Retrieval-Augmented Generation, with a toggle to compare answers with and without retrieval. Documents are chunked and embedded locally with sentence-transformers and stored in an in-memory vector store, so no embedding API key is required. One tab lets you paste text directly into the index, and the chat tab answers questions using the retrieved passages. Launch it with `streamlit run rag_demo.py`.

### [cve_bot.py](cve_bot.py)
A Streamlit chatbot that answers questions about published vulnerabilities using the NIST National Vulnerability Database. It gives a Claude agent two tools: one that lists recent CVEs for a product as a table, and one that summarizes a specific CVE by its ID. The agent picks the right tool based on the question and renders the results inline, including a color-coded severity table. Run it with `streamlit run cve_bot.py`.

### [tool_example.py](tool_example.py)
A small Streamlit agent that shows how to give a model a custom tool. It defines one tool that geolocates a phone number and connects it to Claude through a LangGraph ReAct agent. Ask about a phone number and the agent calls the tool and reports the location. Run it with `streamlit run tool_example.py`.

### [ml_api_example.py](ml_api_example.py)
A FastAPI service that serves a trained machine learning model over HTTP, separate from the language-model examples. It loads a saved domain generation algorithm (DGA) classifier and exposes a `/predict` endpoint that scores a domain string using features such as entropy, digit count, and n-gram frequency. This shows how a model built earlier in the course can be deployed as an API. Start it with `uvicorn ml_api_example:app --reload`, and note that the `DATA_HOME` path near the top must point to your local data directory.

### [tesla_aurora.txt](tesla_aurora.txt)
A short fictional product description used as sample content for the retrieval examples. It describes an invented Tesla vehicle, so questions about it cannot be answered from the model's training data, which makes the effect of retrieval easy to observe. Paste it into `rag_demo.py` to test grounded answers.
