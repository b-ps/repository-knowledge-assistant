from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, BulkIndexError
from repository_knowledge_assistant.ingestion.utils import EmbedChunk
from typing import List

class Index:

    index_name: str

    def __init__(self, host: str = "http://localhost:9200", index_name: str = "repository_chunks"):
        self.client = Elasticsearch(host)
        self.index_name = index_name

    

    def create_index(self):
        if self._exists():
            return

        self.client.indices.create(
            index = self.index_name,
            mappings = {
                "properties": {
                    "path": {"type": "keyword"},
                    "name": {"type": "keyword"},
                    "text": {"type": "text", "similarity": "BM25"},
                    "embedding": {"type": "dense_vector", "similarity": "cosine"}
                }
            }
        )

    def delete_index(self):
        if not self._exists():
            return

        self.client.indices.delete(index = self.index_name)

    def index_documents(self, docs: List[EmbedChunk]):
        actions = [
            {
                "_index": self.index_name,
                "_id": doc.chunk_id,
                "path": str(doc.path),
                "name": doc.name,
                "text": doc.text,
                "embedding": doc.embedding
            }
            for doc in docs
        ]

        try:
            bulk(self.client, actions)
        except BulkIndexError as e: 
            print("Failed to index documents:") 
            for err in e.errors:
                print(err)

    def get_document(self, id: str):
        return self.client.get(index = self.index_name, id = id)

    def text_search(self, query: str):
        response = self.client.search(index = self.index_name, query = {"match": {"text": query}})
        return [
            {
                "id": hit["_id"],
                "score": hit["_score"],
                **hit["_source"],
            }
            for hit in response["hits"]["hits"]
        ]

    def keyword_search(self, keywords: List[str], all: bool = True):
        if all:
            query = {
                "bool": {
                    "must": [{"match": {"text": key}} for key in keywords]
                }
            }
        else:
            query = {
                "bool": {
                    "should": {[{"match": {"text": key}} for key in keywords]}
                }
            }

        response = self.client.search(index = self.index_name, query = query)

        return [
            {
                "id": hit["_id"],
                "score": hit["_score"],
                **hit["_source"],
            }
            for hit in response["hits"]["hits"]
        ]

    def vector_search(self, embed_query: List[float]):
        response = self.client.search(
            index = self.index_name, 
            knn={
                "field": "embedding",
                "query_vector": embed_query,
                "k": 5,
                "num_candidates": 50,
            }
        )
        return [
            {
                "id": hit["_id"],
                "score": hit["_score"],
                **hit["_source"],
            }
            for hit in response["hits"]["hits"]
        ]

    def hybrid_search(self, query: str, embed_query: List[float]):
        text_results = self.text_search(query)
        vector_results = self.vector_search(embed_query)

        rank_constant = 60
        rrf_scores = {}

        # RRF scores from text search
        for rank, result in enumerate(text_results, start=1):
            doc_id = result["id"]

            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = {
                    "score": 0.0,
                    "document": result,
                }

            rrf_scores[doc_id]["score"] += 1 / (rank_constant + rank)

        # RRF scores from vector search
        for rank, result in enumerate(vector_results, start=1):
            doc_id = result["id"]

            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = {
                    "score": 0.0,
                    "document": result,
                }

            rrf_scores[doc_id]["score"] += 1 / (rank_constant + rank)

        # Sort by RRF score
        ranked_results = sorted(
            rrf_scores.values(),
            key=lambda x: x["score"],
            reverse=True,
        )

        # Return results in the same format as your other search methods
        return [
            {
                **item["document"],
                "score": item["score"],
            }
            for item in ranked_results[:5]
        ]

    def _exists(self):
            return self.client.indices.exists(index = self.index_name)