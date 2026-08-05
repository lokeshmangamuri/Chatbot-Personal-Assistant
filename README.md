# Chatbot Personal Assistant

A simple Python-based Retrieval-Augmented Generation (RAG) chatbot / personal assistant that builds embeddings from a document corpus, stores them in a vector store, and uses retrieval + ranking to answer user queries.

This repository contains code for dataloading, embedding, vector storage (Chroma), retrieval, ranking, and a RAG entrypoint.

## What this project includes

- dataloader.py — utilities to load and preprocess documents from the provided corpus.
- documents.txt — the raw document corpus used to build the vector store.
- embedding_model.py — code that generates embeddings for text chunks.
- vector_store.py — wrapper around a vector database (Chroma) to index and query embeddings.
- hybrid_retriever.py — retrieval logic combining semantic and lexical signals.
- ranking.py — re-ranking or scoring logic for retrieved candidates.
- ragmain.py — main script that demonstrates / orchestrates the RAG flow (building embeddings, storing vectors, and answering queries).
- websearch.py — optional web search helper used to augment retrieval with live results.
- pyproject.toml — project metadata and dependencies.
- chroma_db/ — directory expected to hold the Chroma vector database files (if used).

## Requirements

- Python 3.8+ (project is written in Python)
- Project dependencies are listed in pyproject.toml. Install using poetry (if you use it) or extract a requirements list and use pip.

Example using pip (if you have a requirements.txt):

  python -m pip install -r requirements.txt

Or with Poetry:

  poetry install

## Quick start

1. Inspect `documents.txt` to review the corpus used for building the vector store.
2. Prepare any required API keys or configuration your embedding model needs (check `embedding_model.py` for environment variables and model configuration).
3. Build embeddings and the vector store by running:

  python ragmain.py

4. Use the interactive or programmatic interface implemented in the repository to query the assistant. If there is a `main.py` or another entry point, prefer that if it implements a user interface.

## Development notes & context

- This repository uses an on-disk Chroma vector store (see `chroma_db/`) — you can clear and rebuild it by re-running the RAG script that creates the index.
- The `documents.txt` file contains the source knowledge; updating it and re-running the embedding pipeline will refresh the assistant's knowledge.
- `websearch.py` can be used to augment answers with live search results; depending on its implementation you may need API keys for search providers.

## Contributing

Contributions are welcome. Please open an issue or submit a pull request with a clear description of the change.


