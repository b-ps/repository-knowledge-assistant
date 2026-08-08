from repository_knowledge_assistant.repository.clone import RepositoryCloner
from repository_knowledge_assistant.repository.load import RepositoryLoader
from repository_knowledge_assistant.repository.parser import RepositoryParser
from repository_knowledge_assistant.repository.chunk import RepositoryChunker

url = "https://github.com/pypa/sampleproject.git"
repo = RepositoryCloner().get_repository(url)
docs = RepositoryLoader().load(repo)
parser = RepositoryParser()
chunker = RepositoryChunker()
for doc in docs:
    docs2 = parser.parse(doc)
    for doc2 in docs2:
        chunker.chunk(doc2)

