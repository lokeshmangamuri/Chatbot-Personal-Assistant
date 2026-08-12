from dataloader import DataLoader
from embedding_model import EmbeddingModel
from vector_store import VectorStore
from hybrid_retriever import HybridRetriever
from websearch import WebSearcher
from ranking import Reranker
from huggingface_hub import InferenceClient


sources = ["https://arxiv.org/abs/2407.10078",
    # "paper1.pdf",
    # "paper2.pdf",
]
use_web_search = True

loader = DataLoader()

all_documents = []


for source in sources:

    documents = loader.load(source)
    all_documents.extend(documents)


chunks = loader.split_documents(all_documents)

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

    if question.strip().lower() == "exit":
        print("Exiting chatbot...")
        break

    docs = hybrid.invoke(question)

    if use_web_search:
        web_docs = web.search(question)
    else:
        web_docs = []

    all_docs = docs + web_docs

    reranked_docs = ranking.rerank(
        question,
        all_docs,
        k=3
    )

    context = "\n\n".join(
        doc.page_content
        for doc in reranked_docs
    )

    prompt = f"""
You are a helpful assistant.

Answer the question using ONLY the context below.

Context:
{context}

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

    print("\nAnswer:\n")
    print(
        completion.choices[0].message.content
    )