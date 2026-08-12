# Personal Assistant RAG

This project loads and chunks a document, stores its embeddings in a persistent
Chroma vector database, combines dense retrieval with BM25, and reranks the
results alongside web search results before generating an answer.

## Run the interface

Install the project dependencies, then start Streamlit:

```powershell
uv sync
uv run streamlit run app.py
```

The sidebar accepts a document URL or local path. After indexing, use the chat
to search the document, optionally enrich retrieval with web results, and inspect
the reranked sources supporting every answer.

## Vector database

The vector database is managed by `VectorStore` in `vector_store.py` and is
persisted in `chroma_db/`. Document IDs are derived from chunk content and
metadata, so loading the same document again updates the existing vectors
instead of creating duplicates.

```python
from embedding_model import EmbeddingModel
from vector_store import VectorStore

embedding = EmbeddingModel().get_embedding()
store = VectorStore(embedding)
store.add_documents(chunks)

results = store.similarity_search("your question", k=5)
print(store.count())
```

The dense retriever used by the hybrid search pipeline comes from the same
persistent store:

```python
dense_retriever = store.get_dense_retriever(k=5)
```
