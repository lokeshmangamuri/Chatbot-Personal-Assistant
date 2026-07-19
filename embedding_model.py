from langchain_huggingface import HuggingFaceEmbeddings


class EmbeddingModel:

    def __init__(self):

        self.embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2",
        encode_kwargs={"normalize_embeddings": True},)

    def get_embedding(self):

        return self.embedding