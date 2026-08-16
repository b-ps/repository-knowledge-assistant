from .elasticsearch import Index
from ..ingestion.embed import RepositoryEmbedder
from typing import List

class Retriever:

    index: Index
    embedder: RepositoryEmbedder

    def __init__(self, index: Index, embedder: RepositoryEmbedder):
        self.index = index
        self.embedder = embedder


    def retrieve(self, query: str, method: str = "hybrid", top_k: int = 5) -> List[dict]:

        if method == "text":
            return self.index.text_search(query, top_k)

        if method == "vector":
                    embedding = self.embedder.embed_query(query)
                    return self.index.vector_search(embedding, top_k)
    
        if method == "hybrid":
            embedding = self.embedder.embed_query(query)
            return self.index.hybrid_search(query, embedding, top_k)

        raise ValueError(f"Unknown retrieval method: {method}")
