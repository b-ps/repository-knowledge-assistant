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
                "embedding": doc.embedding.tolist()
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

    def vector_search(self, query: List[float]):
        response = self.client.search(index = self.index_name, query = {"match": {"embedding": query}})
        return [
            {
                "id": hit["_id"],
                "score": hit["_score"],
                **hit["_source"],
            }
            for hit in response["hits"]["hits"]
        ]
        

    def _exists(self):
            return self.client.indices.exists(index = self.index_name)