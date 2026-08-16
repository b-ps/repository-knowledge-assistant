from .elasticsearch import Index
from ..ingestion.embed import RepositoryEmbedder

class Retriever:

    index: Index
    embedder: RepositoryEmbedder

    def __init__(self, index: Index, embedder: RepositoryEmbedder):
        self.index = index
        self.embedder = embedder


    def retrieve(self, query: str, method: str = "hybrid"):

        if method == "text":
            return self.index.text_search(query)
    
        if method == "hybrid":
            embedding = self.embedder.embed_query(query)
            return self.index.hybrid_search(query, embedding)
        
        if method == "vector":
            embedding = self.embedder.embed_query(query)
            return self.index.vector_search(embedding)

        raise ValueError(f"Unknown retrieval method: {method}")
