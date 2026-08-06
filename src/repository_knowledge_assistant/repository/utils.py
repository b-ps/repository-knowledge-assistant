from pathlib import Path
from dataclasses import dataclass

@dataclass
class RawDocument:
    path: Path
    text: str
    extension: str

@dataclass
class ParsedDocument:
    text: str
    metadata: dict