"""Streamlit entrypoint: `streamlit run app/main.py`.

`nest_asyncio.apply()` runs at import time so the async LightRAG / RAGAS
calls can share Streamlit's event loop across reruns.
"""

import sys
from pathlib import Path

# `streamlit run app/main.py` puts app/ on sys.path, not the project root,
# so `from app...` imports fail. Prepend the project root before any app.*
# imports.
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import nest_asyncio  # noqa: E402

nest_asyncio.apply()

import asyncio  # noqa: E402

import streamlit as st  # noqa: E402

from app.ingestion.pdf_parser import extract_text_from_pdf  # noqa: E402
from app.rag.engine import create_rag_engine, ingest_text  # noqa: E402

st.set_page_config(page_title="Research Paper Q&A + RAGAS Eval", layout="wide")


def run_async(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


_DEFAULTS = {
    "rag_engine": None,
    "chat_history": [],
    "eval_scores": [],
    "documents_ingested": False,
}
for _key, _default in _DEFAULTS.items():
    if _key not in st.session_state:
        st.session_state[_key] = _default


with st.sidebar:
    st.title("📄 Document Upload")

    uploaded_files = st.file_uploader(
        "Upload research papers (PDF)",
        type=["pdf"],
        accept_multiple_files=True,
    )

    query_mode = st.selectbox(
        "Query Mode",
        options=["naive", "local", "global", "hybrid"],
        index=3,
    )
    st.session_state["query_mode"] = query_mode

    if st.button("🚀 Ingest Documents"):
        if not uploaded_files:
            st.warning("Please upload at least one PDF first.")
        else:
            import tempfile
            from pathlib import Path

            documents: list[str] = []
            with st.spinner("Parsing PDFs..."):
                for uf in uploaded_files:
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".pdf"
                    ) as tmp:
                        tmp.write(uf.getbuffer())
                        tmp_path = Path(tmp.name)
                    try:
                        documents.append(extract_text_from_pdf(str(tmp_path)))
                    finally:
                        tmp_path.unlink(missing_ok=True)

            with st.spinner(
                "Building knowledge graph... This may take a few minutes."
            ):
                rag = run_async(create_rag_engine())
                for doc_text in documents:
                    if doc_text.strip():
                        run_async(ingest_text(rag, doc_text))

            st.session_state["rag_engine"] = rag
            st.session_state["documents_ingested"] = True
            st.session_state["ingested_count"] = len(documents)
            st.success(f"Ingested {len(documents)} document(s).")

    if st.session_state["documents_ingested"]:
        count = st.session_state.get(
            "ingested_count", len(uploaded_files) if uploaded_files else 0
        )
        st.info(f"✅ {count} documents indexed")


st.title("Research Paper Q&A")

if not st.session_state["documents_ingested"]:
    st.info("Upload PDFs in the sidebar to get started")

col1, col2 = st.columns([3, 2])

with col1:
    st.header("💬 Chat")
    st.caption("Chat panel coming soon.")

with col2:
    st.header("📊 Evaluation")
    st.caption("Evaluation panel coming soon.")
