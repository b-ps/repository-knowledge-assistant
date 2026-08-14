from repository_knowledge_assistant.ingestion.clone import RepositoryCloner
from repository_knowledge_assistant.ingestion.load import RepositoryLoader
from repository_knowledge_assistant.ingestion.parse import RepositoryParser
from repository_knowledge_assistant.ingestion.chunk import RepositoryChunker
from repository_knowledge_assistant.ingestion.embed import RepositoryEmbedder
url = "https://github.com/pypa/sampleproject.git"
repo = RepositoryCloner().get_repository(url)
docs = RepositoryLoader().load(repo)
parser = RepositoryParser()
chunker = RepositoryChunker()
chunks = []
for doc in docs:
    docs2 = parser.parse(doc)
    for doc2 in docs2:
        chunks.append(chunker.chunk(doc2))
chunks = sum(chunks, [])

embed = RepositoryEmbedder()
print(embed.embed_documents([chunks[0:2]]))