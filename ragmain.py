from dataloader import DataLoader
from embedding_model import EmbeddingModel
from vector_store import VectorStore
from hybrid_retriever import HybridRetriever


pdf = "https://arxiv.org/pdf/2501.02191"

loader = DataLoader(pdf)

documents = loader.load()

chunks = loader.split_documents(documents)

embedding = EmbeddingModel().get_embedding()

db = VectorStore(embedding)

db.add_documents(chunks)

dense = db.get_dense_retriever()

hybrid = HybridRetriever(chunks, dense).build()

while True:

    question = input("\nQuestion: ")

    docs = hybrid.invoke(question)

    print("=" * 80)

    for i, doc in enumerate(docs):

        print(f"\nChunk {i+1}")

        print(doc.page_content[:700])

        print(doc.metadata)