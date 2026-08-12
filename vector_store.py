import hashlib
import json
from langchain_chroma import Chroma


class VectorStore:
    def __init__(self,embedding,collection_name="paper",persist_directory=None,):

        if persist_directory:
            self.vector_db = Chroma(collection_name=collection_name,persist_directory=str(persist_directory),embedding_function=embedding,)

        else:

            self.vector_db = Chroma(collection_name=collection_name,embedding_function=embedding,)
    def add_documents(self, documents):
        """Add or update chunks without duplicating them across application runs."""
        ids = [self._document_id(document) for document in documents]
        self.vector_db.add_documents(documents=documents, ids=ids)
        return ids

    def similarity_search(self, query, k=5):
        return self.vector_db.similarity_search(query, k=k)

    def count(self):
        return self.vector_db._collection.count()

    def get_dense_retriever(self, k=5):
        return self.vector_db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k},
        )

    @staticmethod
    def _document_id(document):
        payload = json.dumps(
            {
                "content": document.page_content,
                "metadata": document.metadata,
            },
            sort_keys=True,
            default=str,
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()
