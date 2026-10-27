"""
Multi-Document Management & Collection Service for NeuroRead.
Provides batch ingestion, document grouping (collections), and cross-document retrieval.

STRICT RULE: NO TRAINING, NO GRADIENT UPDATES, FROZEN INFERENCE ONLY.
"""

import time
import uuid
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.web.database import (
    create_collection_db,
    list_collections_db,
    delete_collection_db,
    get_db,
)
from src.web.services.pipeline_service import PipelineService


class DocumentService:
    """Manages multi-document lifecycle, collections, batch ingestion, and cross-doc queries."""

    _instance: Optional["DocumentService"] = None

    def __init__(self, pipeline_service: Optional[PipelineService] = None):
        self.pipeline_service = pipeline_service or PipelineService.get_instance()

    @classmethod
    def get_instance(cls) -> "DocumentService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def batch_ingest(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ingests multiple raw text documents in a batch.
        Re-indexes the retriever once at the end for optimal performance.
        """
        store = self.pipeline_service.store
        chunker = self.pipeline_service.chunker
        ingested = []

        now = time.time()
        for item in items:
            title = item.get("title", "").strip() or "Tài liệu chưa đặt tên"
            raw_text = item.get("text", "").strip()
            if not raw_text:
                continue

            doc_id = item.get("document_id") or f"DOC_BATCH_{int(now * 1000)}_{uuid.uuid4().hex[:6]}"
            category = item.get("category", "General")

            # Store or update document
            if doc_id in store._index:
                doc_record = store.update_document(
                    document_id=doc_id,
                    raw_text=raw_text,
                    title=title,
                    metadata={"category": category},
                )
            else:
                doc_record = store.add_document(
                    title=title,
                    raw_text=raw_text,
                    document_id=doc_id,
                    metadata={"category": category},
                )

            # Chunk passages
            passages = chunker.chunk_document(doc_record)
            doc_record.passages = passages
            doc_file = store.docs_dir / doc_id / f"v{doc_record.version}.json"
            with open(doc_file, "w", encoding="utf-8") as f:
                json.dump(doc_record.to_dict(), f, indent=2, ensure_ascii=False)

            words = len(raw_text.split())
            ingested.append({
                "document_id": doc_id,
                "title": title,
                "version": doc_record.version,
                "passage_count": len(passages),
                "word_count": words,
                "token_estimate": int(words * 1.35),
            })

            # Sync to SQLite
            with get_db() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO documents (
                        id, title, category, passage_count, raw_text_preview, created_at, updated_at, version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        doc_id, title, category, len(passages),
                        raw_text[:500], now, now, doc_record.version,
                    ),
                )

        # Batch rebuild index
        self.pipeline_service._initialize_retriever()

        return {
            "success": True,
            "total_ingested": len(ingested),
            "documents": ingested,
        }

    def create_collection(
        self,
        name: str,
        description: str = "",
        document_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Creates a collection and optionally assigns documents to it."""
        coll_id = create_collection_db(name=name, description=description)
        now = time.time()

        if document_ids:
            with get_db() as conn:
                for doc_id in document_ids:
                    conn.execute(
                        "UPDATE documents SET collection_id = ?, updated_at = ? WHERE id = ?",
                        (coll_id, now, doc_id),
                    )

        return {
            "id": coll_id,
            "name": name,
            "description": description,
            "document_ids": document_ids or [],
            "created_at": now,
        }

    def list_collections(self) -> List[Dict[str, Any]]:
        """Lists all collections with their member document counts."""
        raw_colls = list_collections_db()
        result = []
        with get_db() as conn:
            for coll in raw_colls:
                c_id = coll["id"]
                cur = conn.execute(
                    "SELECT id, title FROM documents WHERE collection_id = ?",
                    (c_id,),
                )
                docs = [dict(row) for row in cur.fetchall()]
                result.append({
                    "id": c_id,
                    "name": coll["name"],
                    "description": coll.get("description", ""),
                    "created_at": coll["created_at"],
                    "document_count": len(docs),
                    "documents": docs,
                })
        return result

    def get_collection(self, collection_id: str) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cur = conn.execute("SELECT * FROM collections WHERE id = ?", (collection_id,))
            row = cur.fetchone()
            if not row:
                return None
            row_dict = dict(row)
            doc_cur = conn.execute(
                "SELECT id, title, category, passage_count FROM documents WHERE collection_id = ?",
                (collection_id,),
            )
            docs = [dict(d) for d in doc_cur.fetchall()]
            return {
                "id": row_dict["id"],
                "name": row_dict["name"],
                "description": row_dict.get("description", ""),
                "created_at": row_dict["created_at"],
                "document_count": len(docs),
                "documents": docs,
            }

    def delete_collection(self, collection_id: str) -> bool:
        """Deletes a collection and unlinks documents from it."""
        with get_db() as conn:
            conn.execute(
                "UPDATE documents SET collection_id = NULL WHERE collection_id = ?",
                (collection_id,),
            )
        return delete_collection_db(collection_id)

    def cross_document_retrieve(
        self,
        query: str,
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
    ):
        """Retrieves passages matching query strictly across the given document_ids."""
        return self.pipeline_service.retriever.retrieve(
            query=query,
            top_k=top_k,
            document_ids=document_ids,
        )
