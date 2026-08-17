
from elasticsearch import Elasticsearch


class BaseIndex:

    index_name: str
    mappings: dict = {}

    def __init__(self, host: str = "http://localhost:9200", index_name: str = "repository_chunks_feedback"):
        self.client = Elasticsearch(host)
        self.index_name = index_name

    def create_index(self):
        if self._exists():
            return

        self.client.indices.create(
            index = self.index_name,
            mappings = self.mappings
        )

    def delete_index(self):
        if not self._exists():
            return
        self.client.indices.delete(index = self.index_name)

    def get_document(self, id: str):
        return self.client.get(index = self.index_name, id = id)

    def get_all_documents(self):
        response = self.client.search(index = self.index_name, query = {"match_all": {}})
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