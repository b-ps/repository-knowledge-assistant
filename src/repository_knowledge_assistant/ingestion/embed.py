from sentence_transformers import SentenceTransformer
from .utils import Chunk, EmbedChunk
from typing import List

class RepositoryEmbedder:

    model: SentenceTransformer

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def embed_documents(self, docs: List[Chunk], batch_size = 32) -> List[EmbedChunk]:
        texts = [doc.text for doc in docs]
        embeddings = self.model.encode_document(texts, batch_size = batch_size, normalize_embeddings = True, show_progress_bar = True)
        return [
            EmbedChunk(
                path = doc.path,
                name = doc.name,
                text = doc.text,
                chunk_id = doc.chunk_id,
                embedding = embeddings[i].tolist()
            ) 
            for i, doc in enumerate(docs)
        ]

    def embed_query(self, query: str) -> List[float]:
        return self.model.encode_query(query, normalize_embeddings = True).tolist()