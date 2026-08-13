import os
import tempfile

import streamlit as st
from huggingface_hub import InferenceClient

from dataloader import DataLoader
from embedding_model import EmbeddingModel
from vector_store import VectorStore
from hybrid_retriever import HybridRetriever
from websearch import WebSearcher
from ranking import Reranker


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="RAG BASED Chatbot",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "hybrid" not in st.session_state:
    st.session_state.hybrid = None

if "chunks" not in st.session_state:
    st.session_state.chunks = []

if "db" not in st.session_state:
    st.session_state.db = None

if "ready" not in st.session_state:
    st.session_state.ready = False

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0


# ============================================================
# LOAD MODELS ONLY ONCE
# ============================================================

@st.cache_resource
def load_embedding():
    return EmbeddingModel().get_embedding()


@st.cache_resource
def load_reranker():
    return Reranker()


@st.cache_resource
def load_web_searcher():
    return WebSearcher()


@st.cache_resource
def load_llm():
    return InferenceClient()


embedding = load_embedding()
ranking = load_reranker()
web = load_web_searcher()
client = load_llm()


# ============================================================
# RESET FUNCTION
# ============================================================

def reset_application():

    st.session_state.messages = []
    st.session_state.hybrid = None
    st.session_state.chunks = []
    st.session_state.db = None
    st.session_state.ready = False

    # Change uploader key so uploaded files disappear
    st.session_state.uploader_key += 1

    st.rerun()


# ============================================================
# PROCESS DOCUMENTS
# ============================================================

def process_sources(uploaded_files, urls):

    loader = DataLoader()

    all_documents = []

    # ========================================================
    # Uploaded documents
    # ========================================================

    for uploaded_file in uploaded_files:

        # Get original extension
        suffix = os.path.splitext(uploaded_file.name)[1]

        # Streamlit uploaded files exist in memory.
        # Docling needs a file path, so save temporarily.
        with tempfile.NamedTemporaryFile(delete=False,suffix=suffix) as temp_file:

            temp_file.write(uploaded_file.getbuffer())
            temp_path = temp_file.name

        try:

            documents = loader.load(temp_path)
            for document in documents:
                document.metadata["source"] = uploaded_file.name
            all_documents.extend(documents)

        finally:

            # Delete temporary file after Docling finishes
            if os.path.exists(temp_path):
                os.remove(temp_path)

    for url in urls:
        url = url.strip()
        if not url:
            continue
        documents = loader.load(url)
        all_documents.extend(documents)

    chunks = loader.split_documents(all_documents)
    return chunks




def build_rag(chunks):

    db = VectorStore(embedding)
    db.add_documents(chunks)
    dense = db.get_dense_retriever()
    hybrid = HybridRetriever(chunks,dense).build()
    return db, hybrid


def generate_answer(question, use_web_search):

    docs = []
    # Only retrieve from documents if documents were processed
    if st.session_state.ready and st.session_state.hybrid is not None:
        docs = st.session_state.hybrid.invoke(question)

    if use_web_search:
        web_docs = web.search(question)

    else:
        web_docs = []
    all_docs = docs + web_docs

    if all_docs:
        reranked_docs = ranking.rerank(question,all_docs,k=3)
        context = "\n\n".join(doc.page_content for doc in reranked_docs)
        prompt = f"""
                        You are a helpful assistant.

                        Answer the question using ONLY the context below.

                        If the answer is not available in the context, say that
                        you could not find enough information.

                        Context:
                        {context}

                        Question:
                        {question}
                        """

    else:

        reranked_docs = []

        prompt = f"""
                    You are a helpful assistant.

                    Answer the following question clearly and accurately.

                    Question:
                    {question}
                    """
    completion = client.chat.completions.create(

        model="meta-llama/Llama-3.1-8B-Instruct",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        max_tokens=512,

        temperature=0,
    )

    answer = completion.choices[0].message.content

    return answer, reranked_docs

with st.sidebar:

    st.title("📚 RAG Settings")

    st.write(
        "Upload documents or provide links to build "
        "your knowledge base."
    )

    st.divider()

    st.subheader("📄 Documents")

    uploaded_files = st.file_uploader(
        "Upload documents",
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}",
    )

    st.caption(
        "You can upload multiple documents."
    )

    st.divider()

    st.subheader("🔗 Links")

    urls_text = st.text_area(
        "Enter URLs",
        placeholder=(
            "Enter one URL per line:\n\n"
            "https://arxiv.org/abs/2407.10078\n"
            "https://example.com/document"
        ),
        height=150,
    )

    urls = [
        url.strip()
        for url in urls_text.splitlines()
        if url.strip()
    ]

    st.divider()

    # ========================================================
    # WEB SEARCH
    # ========================================================

    use_web_search = st.toggle(
        "🌐 Use Web Search",
        value=False,
    )

    if use_web_search:

        st.caption(
            "Web search will be combined with "
            "your document retrieval."
        )

    else:

        st.caption(
            "Web search is disabled."
        )

    st.divider()

    if st.button(
        "⚙️ Process Documents",
        type="primary",
        use_container_width=True,):

        if not uploaded_files and not urls:

            st.warning(
                "Upload at least one document "
                "or enter a URL."
            )

        else:

            try:

                with st.spinner(
                    "Loading and chunking documents..."):

                    chunks = process_sources(uploaded_files,urls)

                with st.spinner("Creating vector database..."):

                    db, hybrid = build_rag(chunks)

                # Save everything in session
                st.session_state.chunks = chunks
                st.session_state.db = db
                st.session_state.hybrid = hybrid
                st.session_state.ready = True

                st.success(f"Ready! {len(chunks)} chunks created.")

            except Exception as e:

                st.error(f"Error processing documents: {e}")

    # ========================================================
    # STATUS
    # ========================================================

    if st.session_state.ready:

        st.success("🟢 Knowledge Base Ready")

        st.metric(
            "Chunks",len(st.session_state.chunks))

    else:
        st.info("⚪ No documents processed")

    st.divider()


    if st.button(
        "🗑️ Clear Chat & Documents",
        use_container_width=True,
    ):

        reset_application()


# ============================================================
# MAIN CHATBOT UI
# ============================================================

st.title("🤖 RAG Chatbot")

st.caption(
    "Chat normally, upload documents, or optionally search the web."
)


# ============================================================
# INITIAL MESSAGE
# ============================================================

if not st.session_state.messages:

    with st.chat_message("assistant"):

        if st.session_state.ready:

            st.write(
                "Your documents are ready. "
                "Ask me a question!"
            )

        else:

            st.write(
                "Ask me anything! You can also upload documents "
                "or add links from the sidebar."
            )


# ============================================================
# DISPLAY PREVIOUS CHAT MESSAGES
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        # Display sources for assistant responses
        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            with st.expander("📚 Sources"):

                for i, source in enumerate(
                    message["sources"],
                    start=1
                ):

                    st.markdown(
                        f"**Source {i}**"
                    )

                    st.write(source)


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask a question..."
)


if question:

    if question.strip().lower() == "exit":

        reset_application()

    else:

        # Save user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        # Display user message
        with st.chat_message("user"):

            st.markdown(question)

        with st.chat_message("assistant"):

            try:

                with st.spinner("Thinking..."):

                    answer, retrieved_docs = generate_answer(
                        question,
                        use_web_search
                    )

                # Display answer
                st.markdown(answer)


                source_information = []

                if retrieved_docs:

                    with st.expander(
                        "📚 Retrieved Sources"
                    ):

                        for i, doc in enumerate(
                            retrieved_docs,
                            start=1
                        ):

                            metadata = doc.metadata

                            st.markdown(
                                f"**Source {i}**"
                            )

                            # Web source
                            if metadata.get("source") == "web":

                                st.write(
                                    metadata.get(
                                        "title",
                                        "Web result"
                                    )
                                )

                                st.write(
                                    metadata.get(
                                        "url",
                                        ""
                                    )
                                )

                            # Document source
                            else:

                                st.write(
                                    metadata.get(
                                        "source",
                                        "Document"
                                    )
                                )

                            # Small preview
                            preview = doc.page_content[:300]

                            st.caption(
                                preview + "..."
                            )

                            source_information.append(
                                metadata
                            )


                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": source_information,
                    }
                )

            except Exception as e:

                st.error(
                    f"Error generating answer: {e}"
                )