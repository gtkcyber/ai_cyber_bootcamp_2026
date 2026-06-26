# streamlit_app.py
"""
Streamlit RAG Chat Demo — LangChain + In‑Memory Vector DB (Mac-friendly)

New in this version
- Added a **second tab**: “Add Text” for pasting plain text/paragraphs directly into the vector DB
- Keeps the original “Chat” tab with RAG ON/OFF toggle
- Still uses **LangChain** + **DocArrayInMemorySearch** (pure in‑memory)

Setup
1) Python 3.10+
2) pip install -r requirements.txt (see bottom of file)
3) Export your OpenAI API key (macOS/Linux):
   export OPENAI_API_KEY=sk-...
4) (Optional) Put .txt/.md/.pdf files into ./docs and click “Rebuild index” — OR just paste text in the “Add Text” tab.
5) Run: streamlit run streamlit_app.py
"""

from __future__ import annotations
import os
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
from typing import List, Dict, Tuple

import streamlit as st

# ---- LangChain core components ----
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain.schema import Document

# Optional PDF support (still supported, but now optional)
try:
    import pypdf
    HAS_PDF = True
except Exception:
    HAS_PDF = False

DOCS_DIR = Path("docs")
DEFAULT_MODEL = os.getenv("RAG_CHAT_MODEL", "gpt-4o-mini")
EMBED_MODEL = os.getenv("RAG_EMBED_MODEL", "text-embedding-3-small")

# --------------------------- Utilities ---------------------------

def require_api_key() -> bool:
    if os.getenv("OPENAI_KEY") in (None, ""):
        st.error("OPENAI_KEY is not set. Please set it in your environment and rerun.")
        with st.expander("How to set it on macOS/Linux"):
            st.code("""# mac/linux
env | grep OPENAI_KEY  # optional check
export OPENAI_KEY=sk-...""", language="bash")
        return False
    return True


def read_txt_or_md(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def read_pdf(path: Path) -> str:
    if not HAS_PDF:
        return ""
    try:
        reader = pypdf.PdfReader(str(path))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return ""


def load_documents() -> List[Document]:
    docs: List[Document] = []
    DOCS_DIR.mkdir(exist_ok=True)
    for p in DOCS_DIR.glob("**/*"):
        if not p.is_file():
            continue
        text = ""
        if p.suffix.lower() in {".txt", ".md"}:
            text = read_txt_or_md(p)
        elif p.suffix.lower() == ".pdf":
            text = read_pdf(p)
        if text and text.strip():
            docs.append(Document(page_content=text, metadata={"source": str(p)}))
    return docs


def chunk_documents(docs: List[Document], *, chunk_size: int = 2000, chunk_overlap: int = 300) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,  # ~500 tokens
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True,
    )
    return splitter.split_documents(docs)


def get_embeddings() -> OpenAIEmbeddings:
    if "embeddings" not in st.session_state:
        st.session_state.embeddings = OpenAIEmbeddings(model=EMBED_MODEL, api_key=os.getenv("OPENAI_KEY"))
    return st.session_state.embeddings


# --------------------------- Vector Store (in-memory) ---------------------------

def build_vectorstore() -> Tuple[DocArrayInMemorySearch | None, List[Document]]:
    """Build from ./docs (if any). Returns (vectorstore, chunks)."""
    base_docs = load_documents()
    if not base_docs:
        # no warning here; "Add Text" tab can be used instead
        return None, []

    chunks = chunk_documents(base_docs)
    vs = DocArrayInMemorySearch.from_documents(chunks, embedding=get_embeddings())
    return vs, chunks


def get_vectorstore() -> Tuple[DocArrayInMemorySearch | None, List[Document]]:
    vs = st.session_state.get("vectorstore")
    chunks = st.session_state.get("chunks", [])
    return vs, chunks


def add_chunks_to_vectorstore(chunks: List[Document]):
    if not chunks:
        return
    vs = st.session_state.get("vectorstore")
    if vs is None:
        st.session_state.vectorstore = DocArrayInMemorySearch.from_documents(chunks, embedding=get_embeddings())
    else:
        vs.add_documents(chunks, embedding=get_embeddings())
    # Track chunks if you want to display them later
    st.session_state.chunks = st.session_state.get("chunks", []) + chunks


# --------------------------- RAG Helpers ---------------------------

def retrieve(vs: DocArrayInMemorySearch | None, query: str, k: int) -> List[Document]:
    if vs is None:
        return []
    return vs.similarity_search(query, k=k)


def format_context(snippets: List[Document]) -> str:
    blocks = []
    for i, d in enumerate(snippets, 1):
        src = Path(d.metadata.get("source", "?"))
        blocks.append(f"[Source {i}: {src.name}]\n{d.page_content}")
    return "\n\n".join(blocks)


# --------------------------- Generation ---------------------------
SYS_NO_RAG = "You are a concise, helpful teaching assistant."
SYS_WITH_RAG = (
    "You are a helpful teaching assistant. Use ONLY the provided context to answer. "
    "If the answer is not in the context, say you don't know."
)

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", SYS_WITH_RAG + "\n\nContext:\n{context}"),
    ("human", "{question}"),
])


def chat_no_rag(llm: ChatOpenAI, history: List[Dict[str, str]], user_prompt: str) -> str:
    messages = [SystemMessage(content=SYS_NO_RAG)]
    for m in history:
        role = m["role"]
        content = m["content"]
        if role == "user":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))
    messages.append(HumanMessage(content=user_prompt))
    resp = llm.invoke(messages)
    return resp.content


def chat_with_rag(llm: ChatOpenAI, vs: DocArrayInMemorySearch | None, user_prompt: str, k: int) -> Tuple[str, List[Document]]:
    retrieved = retrieve(vs, user_prompt, k=k)
    context = format_context(retrieved) if retrieved else ""
    chain = qa_prompt | llm
    answer = chain.invoke({"context": context, "question": user_prompt}).content
    return answer, retrieved


# --------------------------- Streamlit UI ---------------------------

def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []  # [{role, content}]


def sidebar(llm: ChatOpenAI) -> Tuple[bool, int]:
    st.sidebar.header("RAG Settings")
    use_rag = st.sidebar.toggle("Use RAG", value=True)
    top_k = st.sidebar.slider("Top-K passages", min_value=2, max_value=10, value=4, step=1)

    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Rebuild index"):
            vs, chunks = build_vectorstore()
            st.session_state.vectorstore = vs
            st.session_state.chunks = chunks
            st.success("Index rebuilt in memory from ./docs.")
    with col2:
        if st.button("Clear chat"):
            st.session_state.messages = []

    with st.sidebar.expander("Corpus status"):
        vs, chunks = get_vectorstore()
        num_docs = len(chunks)
        st.markdown(f"**Documents in memory:** {num_docs}")
        if st.button("Clear in‑memory corpus"):
            st.session_state.vectorstore = None
            st.session_state.chunks = []
            st.success("Cleared in‑memory vector DB.")

    st.sidebar.caption("Docs folder: ./docs  |  Vector DB: in‑memory (DocArray)")
    return use_rag, top_k


def show_sources(snippets: List[Document]):
    if not snippets:
        return
    with st.expander("Show retrieved sources"):
        for i, d in enumerate(snippets, 1):
            src = d.metadata.get("source", "?")
            st.markdown(f"**Source {i}:** `{src}`")
            st.write(d.page_content)
            st.markdown("---")


def add_text_tab_ui():
    st.subheader("Add Text to Vector DB")
    st.caption("Paste any plain text. We'll chunk it and add to the in‑memory vector store.")

    with st.form("add_text_form", clear_on_submit=False):
        title = st.text_input("Title / Source label", placeholder="e.g., 'Lecture notes – RAG basics'")
        raw_text = st.text_area("Paste text here", height=240, placeholder="Paste one or more paragraphs…")
        c1, c2 = st.columns(2)
        with c1:
            chunk_size = st.slider("Chunk size (chars)", 500, 4000, 2000, 100)
        with c2:
            chunk_overlap = st.slider("Chunk overlap (chars)", 0, 800, 300, 50)
        submitted = st.form_submit_button("Add to Vector DB")

    if submitted:
        if not raw_text.strip():
            st.warning("Please paste some text first.")
            return
        label = title.strip() or raw_text.strip()[:40] + ("…" if len(raw_text.strip()) > 40 else "")
        base_doc = Document(page_content=raw_text, metadata={"source": f"clipboard:{label}"})
        chunks = chunk_documents([base_doc], chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        add_chunks_to_vectorstore(chunks)
        st.success(f"Added {len(chunks)} chunk(s) from '{label}' to the vector DB.")

    # Preview what we have in memory
    vs, chunks = get_vectorstore()
    st.markdown("---")
    st.markdown(f"**Current in‑memory documents:** {len(chunks)}")
    if chunks:
        with st.expander("Preview first few chunks"):
            for i, d in enumerate(chunks[:5], 1):
                st.markdown(f"**Chunk {i}** — `{d.metadata.get('source', '?')}`")
                st.write(d.page_content)
                st.markdown("---")


def chat_tab_ui(llm: ChatOpenAI, use_rag: bool, top_k: int):
    # Chat history UI
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Ask me about the docs… or anything if RAG is off")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if use_rag:
                vs, _ = get_vectorstore()
                if vs is None:
                    st.info("No vector index yet. Add text in the 'Add Text' tab or click 'Rebuild index'.")
                    answer = chat_no_rag(llm, st.session_state.messages, prompt)
                else:
                    answer, retrieved = chat_with_rag(llm, vs, prompt, k=top_k)
                    st.markdown(answer)
                    show_sources(retrieved)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    return
            else:
                answer = chat_no_rag(llm, st.session_state.messages, prompt)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})


def main():
    st.set_page_config(page_title="RAG Chat Demo (LangChain)", page_icon="🧩", layout="wide")
    st.title("🧩 RAG Chat Demo — LangChain + In‑Memory Vector DB")
    st.caption("Toggle Retrieval-Augmented Generation on/off in the sidebar.")

    if not require_api_key():
        st.stop()

    llm = ChatOpenAI(model=DEFAULT_MODEL, temperature=0.2, api_key=os.getenv("OPENAI_KEY"))
    init_state()

    use_rag, top_k = sidebar(llm)

    # Tabs: Chat | Add Text
    chat_tab, add_text_tab = st.tabs(["💬 Chat", "🧾 Add Text"])

    with chat_tab:
        chat_tab_ui(llm, use_rag, top_k)

    with add_text_tab:
        add_text_tab_ui()


if __name__ == "__main__":
    main()
