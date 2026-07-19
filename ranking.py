from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("COHERE_API_KEY")
from langchain_cohere import CohereRerank


class Reranker:

    def __init__(self):

        self.reranker = CohereRerank(model="rerank-v3.5")

    def rerank(self, query, documents,k=2):

        reranked_docs=self.reranker.compress_documents(documents=documents,query=query,)
        return reranked_docs[:k]