from dataloader import DataLoader
from embedding_model import EmbeddingModel
from vector_store import VectorStore
from hybrid_retriever import HybridRetriever
from websearch import WebSearcher
from ranking import Reranker
from huggingface_hub import InferenceClient


pdf = "https://arxiv.org/abs/2407.10078"

loader = DataLoader(pdf)

documents = loader.load()

chunks = loader.split_documents(documents)

embedding = EmbeddingModel().get_embedding()

db = VectorStore(embedding)

db.add_documents(chunks)

dense = db.get_dense_retriever()

hybrid = HybridRetriever(chunks, dense).build()
web = WebSearcher()
ranking= Reranker()
client = InferenceClient()


while True:

    question = input("\nQuestion: ")
    docs = hybrid.invoke(question)
    web_docs = web.search(question)
    all_docs = docs+ web_docs
    reranked_docs = ranking.rerank(question,all_docs,k=3)
    for i, doc in enumerate(reranked_docs, start=1):
        print(f"\nDocument {i}")
        print(doc.metadata)
    context = "\n\n".join(doc.page_content for doc in reranked_docs)
    prompt = f"""You are a helpful assistant.Answer the question using ONLY the context below.Context:{context}Question:{question}"""
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

    print("\nAnswer:\n")
    print(completion.choices[0].message.content)
