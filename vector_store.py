from langchain_chroma import Chroma


class VectorStore:

    def __init__(self, embedding):

        self.vector_db = Chroma(
            collection_name="paper",
            persist_directory="./chroma_db",
            embedding_function=embedding,
        )

    def add_documents(self, documents):

        self.vector_db.add_documents(documents)

    def get_dense_retriever(self):

        return self.vector_db.as_retriever(search_type="similarity",
            search_kwargs={"k": 5},)