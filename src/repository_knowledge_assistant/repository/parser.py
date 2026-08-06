from .utils import RawDocument, ParsedDocument
from typing import List
import re
import ast

HEADER_PATTERN = re.compile(r"^\s*(#{1,2})\s+(.+)$")

class RepositoryParser:

    PARSERS = {
        ".md": "_parse_markdown",
        ".py": "_parse_python",
    }

    def parse(self, document: RawDocument):
        parser_name = self.PARSERS.get(document.extension, "_parse_default")
        parser = getattr(self, parser_name)

        return parser(document)

    def _parse_markdown(self, document: RawDocument) -> List[ParsedDocument]:
        """
        Split a markdown document into sections based on headings.
        """

        sections = []
        current_content = []
        current_title = {}
        current_level = 0

        for line in document.text.splitlines():
            match = HEADER_PATTERN.match(line)

            if match:
                # Save previous section
                if current_content:
                    sections.append(
                        ParsedDocument(
                            text = "\n".join(current_content).strip(),
                            metadata = {
                                "path": str(document.path),
                                "title": current_title[current_level],
                                "level": current_level,
                                "type": "markdown_section"
                                }
                        )
                    )

                # New section
                current_level = len(match.group(1))
                current_title = {k: v for k, v in current_title.items() if k < current_level}
                current_title[current_level] = match.group(2).strip()
                current_content.append(f"Section: {" > ".join(list(current_title.values()))}\n")

            else:
                current_content.append(line)

        # Save last section
        if current_content:
            sections.append(
                ParsedDocument(
                    text = "\n".join(current_content).strip(),
                    metadata = {
                        "path": str(document.path),
                        "title": current_title[current_level],
                        "level": current_level,
                        "type": "markdown_section"
                        }
                )
            )

    def _parse_python(self, document: RawDocument) -> List[ParsedDocument]:
        module = ast.parse(document.text)
        documents = []
        other_code = []
        for node in module.body:
            if isinstance(node, ast.ClassDef):
                documents.append(
                    ParsedDocument(
                        text = ast.get_source_segment(document.text, node).strip(),
                        metadata = {
                            "path": str(document.path),
                            "title": node.name,
                            "type": "python_class"
                        }
                    )
                )
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                documents.append(
                    ParsedDocument(
                        text = ast.get_source_segment(document.text, node).strip(),
                        metadata = {
                            "path": str(document.path),
                            "title": node.name,
                            "type": "python_function"
                        }
                    )
                )
            else:
                other_code.append(ast.get_source_segment(document.text, node))

        if other_code:
            documents.append(
                ParsedDocument(
                    text = "\n".join(other_code).strip(),
                    metadata = {
                        "path": str(document.path),
                        "title": document.path.name,
                        "type": "python_module"
                    }
                )
            )

    def _parse_default(self, document: RawDocument) -> List[ParsedDocument]:
        """
        Default parser for other file types.
        Return the whole file as a single ParsedDocument.
        """

        return [
            ParsedDocument(
                text = document.text,
                metadata = {
                    "path": str(document.path),
                    "title": document.path.name,
                    "type": "raw_file",
                },
            )
        ]