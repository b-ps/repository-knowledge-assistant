from .chunk import RepositoryChunker
from .clone import RepositoryCloner
from .load import RepositoryLoader
from .parse import RepositoryParser
from .embed import RepositoryEmbedder
from ..search.elasticsearch import Index

from prefect import flow, task

@task(retries=3, retry_delay_seconds=30)
def get_repository(repository_url: str):
    """Clone or update the repository and return its local path."""
    cloner = RepositoryCloner() 
    return cloner.get_repository(repository_url)


@task
def process_documents(repository_path):
    """Parse repository files and split them into chunks."""
    loader = RepositoryLoader()
    parser = RepositoryParser()
    chunker = RepositoryChunker()

    raw_documents = loader.load(repository_path)
    
    chunks = []

    for doc in raw_documents:
        parsed_documents = parser.parse(doc)

        for pdoc in parsed_documents:
            chunks.extend(chunker.chunk(pdoc))

    return chunks

@task
def embed_documents(chunks, model: str):
    """Generate embeddings for all repository chunks."""
    embedder = RepositoryEmbedder(model)
    return embedder.embed_documents(chunks)

@task(retries=3, retry_delay_seconds=30)
def index_documents(index_name: str, documents):
    """Store embedded documents in an Elasticsearch index."""
    index = Index(index_name = index_name)
    index.create_index()
    index.index_documents(documents)

@flow(name="repository-ingestion")
def ingestion(repository_url: str, local_path: str = "repository-knowledge-assistant/data/repos", model: str = "all-MiniLM-L6-v2", index_name = "sample_project"):
    """Ingest a GitHub repository into the Elasticsearch knowledge base."""

    repository_path = get_repository(repository_url)

    chunks = process_documents(repository_path)

    embedded_chunks = embed_documents(chunks, model)

    index_documents(index_name, embedded_chunks)
    

if __name__ == "__main__":
    ingestion(
        repository_url="https://github.com/pypa/sampleproject.git"
    )

