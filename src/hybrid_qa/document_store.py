"""
Document Store — manages a corpus of documents with versioning, structural
parsing, chunking, and SA-CMS memory snapshot linkage.

Design decisions:
- Filesystem/JSON backed (simple, reproducible, no DB dependency).
- Each document gets a unique ID and immutable version chain.
- Passages get globally-unique IDs in format DOC{id}::P{idx}.
- Memory snapshots are tied to (document_id, version) pairs.
"""

import json
import hashlib
import time
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class Passage:
    """A retrievable text passage within a document."""
    passage_id: str          # e.g. "DOC001::P003"
    document_id: str
    text: str
    start_char: int
    end_char: int
    start_token: int = -1
    end_token: int = -1
    section_title: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Passage":
        return cls(**d)


@dataclass
class DocumentRecord:
    """A single version of a document in the store."""
    document_id: str
    version: int
    title: str
    raw_text: str
    passages: List[Passage] = field(default_factory=list)
    structural_metadata: Dict[str, Any] = field(default_factory=dict)
    content_hash: str = ""
    created_at: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = hashlib.sha256(self.raw_text.encode("utf-8")).hexdigest()[:16]
        if self.created_at == 0.0:
            self.created_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["passages"] = [p.to_dict() if isinstance(p, Passage) else p for p in self.passages]
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DocumentRecord":
        passages = [Passage.from_dict(p) if isinstance(p, dict) else p for p in d.get("passages", [])]
        d = dict(d)
        d["passages"] = passages
        return cls(**d)


class DocumentStore:
    """
    Manages a corpus of documents on the filesystem.
    
    Directory layout:
        store_dir/
            index.json          # {doc_id: {version, title, content_hash}}
            documents/
                DOC001/
                    v1.json     # Full DocumentRecord
                    v2.json
                DOC002/
                    v1.json
            snapshots/
                DOC001_v1.pt    # SA-CMS memory checkpoint
    """

    def __init__(self, store_dir: str = "data/document_store"):
        self.store_dir = Path(store_dir)
        self.docs_dir = self.store_dir / "documents"
        self.snapshots_dir = self.store_dir / "snapshots"
        self.index_path = self.store_dir / "index.json"

        # Create directories
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

        # Load or initialize index
        self._index: Dict[str, Dict[str, Any]] = {}
        self._load_index()

    def _load_index(self):
        if self.index_path.exists():
            with open(self.index_path, "r", encoding="utf-8") as f:
                self._index = json.load(f)
        else:
            self._index = {}
            self._save_index()

    def _save_index(self):
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(self._index, f, indent=2, ensure_ascii=False)

    def _next_doc_id(self) -> str:
        existing_nums = []
        for doc_id in self._index:
            try:
                existing_nums.append(int(doc_id.replace("DOC", "")))
            except ValueError:
                pass
        next_num = max(existing_nums, default=0) + 1
        return f"DOC{next_num:03d}"

    def add_document(
        self,
        title: str,
        raw_text: str,
        document_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DocumentRecord:
        """Add a new document to the store. Returns the created DocumentRecord."""
        if document_id is None:
            document_id = self._next_doc_id()

        if document_id in self._index:
            raise ValueError(f"Document {document_id} already exists. Use update_document() instead.")

        record = DocumentRecord(
            document_id=document_id,
            version=1,
            title=title,
            raw_text=raw_text,
            metadata=metadata or {},
        )

        # Save document file
        doc_dir = self.docs_dir / document_id
        doc_dir.mkdir(parents=True, exist_ok=True)
        doc_path = doc_dir / "v1.json"
        with open(doc_path, "w", encoding="utf-8") as f:
            json.dump(record.to_dict(), f, indent=2, ensure_ascii=False)

        # Update index
        self._index[document_id] = {
            "current_version": 1,
            "title": title,
            "content_hash": record.content_hash,
            "created_at": record.created_at,
        }
        self._save_index()

        return record

    def update_document(
        self,
        document_id: str,
        raw_text: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DocumentRecord:
        """Create a new version of an existing document."""
        if document_id not in self._index:
            raise KeyError(f"Document {document_id} not found.")

        current_version = self._index[document_id]["current_version"]
        new_version = current_version + 1

        record = DocumentRecord(
            document_id=document_id,
            version=new_version,
            title=title or self._index[document_id]["title"],
            raw_text=raw_text,
            metadata=metadata or {},
        )

        # Save new version
        doc_dir = self.docs_dir / document_id
        doc_path = doc_dir / f"v{new_version}.json"
        with open(doc_path, "w", encoding="utf-8") as f:
            json.dump(record.to_dict(), f, indent=2, ensure_ascii=False)

        # Update index
        self._index[document_id]["current_version"] = new_version
        self._index[document_id]["content_hash"] = record.content_hash
        self._save_index()

        return record

    def get_document(self, document_id: str, version: Optional[int] = None) -> DocumentRecord:
        """Retrieve a document by ID. If version is None, returns the latest."""
        if document_id not in self._index:
            raise KeyError(f"Document {document_id} not found.")

        if version is None:
            version = self._index[document_id]["current_version"]

        doc_path = self.docs_dir / document_id / f"v{version}.json"
        if not doc_path.exists():
            raise FileNotFoundError(f"Version {version} of {document_id} not found.")

        with open(doc_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return DocumentRecord.from_dict(data)

    def remove_document(self, document_id: str) -> bool:
        """Remove a document and all its versions from the store."""
        if document_id not in self._index:
            return False

        import shutil
        doc_dir = self.docs_dir / document_id
        if doc_dir.exists():
            shutil.rmtree(doc_dir)

        # Remove associated snapshots
        for snapshot_file in self.snapshots_dir.glob(f"{document_id}_*.pt"):
            snapshot_file.unlink()

        del self._index[document_id]
        self._save_index()
        return True

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the store with summary info."""
        result = []
        for doc_id, info in self._index.items():
            result.append({
                "document_id": doc_id,
                "title": info["title"],
                "current_version": info["current_version"],
                "content_hash": info["content_hash"],
            })
        return result

    def save_memory_snapshot(self, document_id: str, version: int, snapshot_data: Any) -> str:
        """Save an SA-CMS memory snapshot tied to a specific document version."""
        import torch
        snapshot_path = self.snapshots_dir / f"{document_id}_v{version}.pt"
        torch.save(snapshot_data, str(snapshot_path))
        return str(snapshot_path)

    def load_memory_snapshot(self, document_id: str, version: int) -> Any:
        """Load an SA-CMS memory snapshot for a specific document version."""
        import torch
        snapshot_path = self.snapshots_dir / f"{document_id}_v{version}.pt"
        if not snapshot_path.exists():
            raise FileNotFoundError(f"No memory snapshot for {document_id} v{version}")
        return torch.load(str(snapshot_path), map_location="cpu")

    def has_memory_snapshot(self, document_id: str, version: int) -> bool:
        """Check if a memory snapshot exists."""
        snapshot_path = self.snapshots_dir / f"{document_id}_v{version}.pt"
        return snapshot_path.exists()

    def get_all_passages(self, document_id: Optional[str] = None) -> List[Passage]:
        """Get all passages, optionally filtered by document_id."""
        passages = []
        doc_ids = [document_id] if document_id else list(self._index.keys())
        for did in doc_ids:
            try:
                doc = self.get_document(did)
                passages.extend(doc.passages)
            except (KeyError, FileNotFoundError):
                continue
        return passages

    @property
    def document_count(self) -> int:
        return len(self._index)
