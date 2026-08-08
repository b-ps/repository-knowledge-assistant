from .utils import Chunk, ParsedDocument
from typing import List


MAX_CHAR = 2500


class RepositoryChunker:

    CHUNKERS = {
            "markdown_section": "_chunk_markdown",
            "python_class": "_chunk_python",
            "python_function": "_chunk_python",
            "python_module": "_chunk_python"
        }

    def chunk(self, document: ParsedDocument) -> List[Chunk]:
        chunker_name = self.CHUNKERS.get(document.metadata['type'], "_chunk_default")
        chunker = getattr(self, chunker_name)

        return chunker(document)

    def _chunk_markdown(self, document: ParsedDocument) -> List[Chunk]:
        title = "\n".join(document.text.splitlines()[:2])
        char = len(title)
        chunks = []
        current_content = [title]
        current_paragraph = []
        i = 0
        for line in document.text.splitlines()[2:]:
            if line == '':
                current_paragraph.append(line)
                paragraph = "\n".join(current_paragraph)
                char += len(paragraph)

                if char > MAX_CHAR:
                    chunks.append(
                        Chunk(
                            path = document.path,
                            name = document.name,
                            text = "\n".join(current_content + ['(...)']),
                            chunk_id = f"{document.doc_id}_c{i}"
                        )
                    )
                    current_content = [title, '(...)\n', paragraph]
                    char = len(title) + len(paragraph)
                    i += 1
                else:
                    current_content.append(paragraph)

                current_paragraph = []
            else:
                current_paragraph.append(line)

        paragraph = "\n".join(current_paragraph)
        char += len(paragraph)
        
        if char > MAX_CHAR:
            chunks.append(
                Chunk(
                    path = document.path,
                    name = document.name,
                    text = "\n".join(current_content + ['(...)']),
                    chunk_id = f"{document.doc_id}_c{i}"
                )
            )
            i += 1
            current_content = [title, '(...)\n', paragraph]
            chunks.append(
                Chunk(
                    path = document.path,
                    name = document.name,
                    text = "\n".join(current_content),
                    chunk_id = f"{document.doc_id}_c{i}"
                )
            )
        
        else:
            current_content.append(paragraph)
            chunks.append(
                Chunk(
                    path = document.path,
                    name = document.name,
                    text = "\n".join(current_content).strip(),
                    chunk_id = f"{document.doc_id}_c{i}"
                )
            )


        return chunks      

    def _chunk_python(self, document: ParsedDocument) -> List[Chunk]:
        # TODO
        return self._chunk_default(document)
    
    def _chunk_default(self, document: ParsedDocument) -> List[Chunk]:

        char = 0
        chunks = []
        current_content = []
        current_paragraph = []
        i = 0

        for line in document.text.splitlines():
            if line == '':
                current_paragraph.append(line)
                paragraph = "\n".join(current_paragraph)
                char += len(paragraph)
            
                if char > MAX_CHAR:
                    chunks.append(
                        Chunk(
                            path = document.path,
                            name = document.name,
                            text = "\n".join(current_content + ['(...)']),
                            chunk_id = f"{document.doc_id}_c{i}"
                        )
                    )
                    current_content = ['(...)\n', paragraph]
                    char = len(paragraph)
                    i += 1
            
                else:
                    current_content.append(paragraph)
            
                current_paragraph = []
            else:
                current_paragraph.append(line)

        paragraph = "\n".join(current_paragraph)
        char += len(paragraph)
        
        if char > MAX_CHAR:
            chunks.append(
                Chunk(
                    path = document.path,
                    name = document.name,
                    text = "\n".join(current_content + ['(...)']),
                    chunk_id = f"{document.doc_id}_c{i}"
                )
            )
            i += 1
            current_content = ['(...)\n', paragraph]
            chunks.append(
                Chunk(
                    path = document.path,
                    name = document.name,
                    text = "\n".join(current_content),
                    chunk_id = f"{document.doc_id}_c{i}"
                )
            )
        
        else:
            current_content.append(paragraph)
            chunks.append(
                Chunk(
                    path = document.path,
                    name = document.name,
                    text = "\n".join(current_content).strip(),
                    chunk_id = f"{document.doc_id}_c{i}"
                )
            )


        return chunks      