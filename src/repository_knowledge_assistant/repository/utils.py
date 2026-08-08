from pathlib import Path
from dataclasses import dataclass

@dataclass
class RawDocument:
    path: Path
    text: str
    extension: str
    name: str
    raw_doc_id: str

@dataclass
class ParsedDocument:
    path: Path
    text: str
    name: str
    doc_id: str
    metadata: dict
    

@dataclass
class Chunk:
    path: Path
    name: str
    text: str
    chunk_id: str
    