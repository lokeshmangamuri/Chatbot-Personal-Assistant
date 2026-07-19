from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
class HybridRetriever:

    def __init__(self, documents, dense_retriever):

        self.documents = documents
        self.dense = dense_retriever

    def build(self):

        bm25 = BM25Retriever.from_documents(self.documents)
        bm25.k = 5

        hybrid = EnsembleRetriever(
            retrievers=[bm25,self.dense,],weights=[0.5,0.5,],)

        return hybrid