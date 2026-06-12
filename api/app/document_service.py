from pathlib import PurePath
import re
from typing import Literal
from uuid import UUID

import fitz
from fastapi import HTTPException
from supabase import Client

DocumentType = Literal["resume", "role_description"]


class DocumentService:
    def __init__(self, supabase: Client) -> None:
        self.supabase = supabase
        self.bucket_name = "interview-documents"
        self._text_store: dict[tuple[str, DocumentType], str] = {}

    def process_document(
        self,
        interview_id: UUID,
        document_type: DocumentType,
        filename: str,
        content_type: str | None,
        file_bytes: bytes,
    ) -> dict:
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        if content_type and content_type not in {
            "application/pdf",
            "application/x-pdf",
        }:
            raise HTTPException(status_code=400, detail="Invalid file content type")

        extracted_text = self._extract_text_from_pdf(file_bytes)
        extracted_character_count = len(extracted_text)
        original_filename = self._normalize_original_filename(filename)
        normalized_filename = self._to_snake_case_filename(original_filename)
        self._validate_not_already_uploaded(
            interview_id=interview_id,
            document_type=document_type,
            filename=normalized_filename,
        )

        storage_path = self._upload_to_supabase_storage(
            interview_id=interview_id,
            document_type=document_type,
            filename=normalized_filename,
            file_bytes=file_bytes,
        )

        self._upsert_document_record(
            interview_id=interview_id,
            document_type=document_type,
            filename=normalized_filename,
            storage_path=storage_path,
            mime_type=content_type or "application/pdf",
            extracted_text=extracted_text,
            extracted_character_count=extracted_character_count,
        )

        self._text_store[(str(interview_id), document_type)] = extracted_text

        return {
            "interview_id": interview_id,
            "document_type": document_type,
            "extracted_character_count": extracted_character_count,
            "storage_path": storage_path,
        }

    def get_extracted_text(
        self, interview_id: UUID, document_type: DocumentType
    ) -> str | None:
        return self._text_store.get((str(interview_id), document_type))

    def list_document_names(self, interview_id: UUID) -> list[str]:
        document_names: list[str] = []
        for document_type in ("resume", "role_description"):
            folder = f"{interview_id}/{document_type}"
            try:
                items = self.supabase.storage.from_(self.bucket_name).list(path=folder)
            except Exception as exc:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Could not list files from Supabase Storage. "
                        "Ensure bucket 'interview-documents' exists."
                    ),
                ) from exc

            for item in items or []:
                name = item.get("name") if isinstance(item, dict) else None
                if not name:
                    continue
                document_names.append(f"{document_type}/{name}")

        return sorted(document_names)

    def list_documents_from_table(self, interview_id: UUID) -> list[dict]:
        response = (
            self.supabase.table("documents")
            .select(
                "id,interview_id,document_type,filename,storage_path,mime_type,"
                "extracted_text,extracted_character_count,created_at"
            )
            .eq("interview_id", str(interview_id))
            .order("created_at", desc=False)
            .execute()
        )
        return response.data or []

    def delete_document(self, interview_id: UUID, filename: str) -> dict:
        original_filename = self._normalize_original_filename(filename)
        normalized_filename = self._to_snake_case_filename(original_filename)
        response = (
            self.supabase.table("documents")
            .select("id,document_type,filename,storage_path")
            .eq("interview_id", str(interview_id))
            .eq("filename", normalized_filename)
            .execute()
        )
        matches = response.data or []
        if not matches:
            raise HTTPException(status_code=404, detail="Document not found")
        if len(matches) > 1:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Multiple documents found with the same filename for this interview. "
                    "Use unique filenames per document type."
                ),
            )

        document = matches[0]
        document_id = document.get("id") if isinstance(document, dict) else None
        storage_path = (
            document.get("storage_path") if isinstance(document, dict) else None
        )
        document_type = (
            document.get("document_type") if isinstance(document, dict) else None
        )
        if not document_id or not storage_path:
            raise HTTPException(status_code=500, detail="Corrupted document metadata")

        try:
            self.supabase.storage.from_(self.bucket_name).remove([storage_path])
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Could not delete file from Supabase Storage",
            ) from exc

        try:
            self.supabase.table("documents").delete().eq("id", document_id).execute()
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Could not delete document metadata from database",
            ) from exc

        if document_type == "resume":
            self._text_store.pop((str(interview_id), "resume"), None)
        elif document_type == "role_description":
            self._text_store.pop((str(interview_id), "role_description"), None)

        return {
            "interview_id": interview_id,
            "filename": normalized_filename,
            "deleted": True,
        }

    def _upsert_document_record(
        self,
        interview_id: UUID,
        document_type: DocumentType,
        filename: str,
        storage_path: str,
        mime_type: str,
        extracted_text: str,
        extracted_character_count: int,
    ) -> None:
        payload = {
            "interview_id": str(interview_id),
            "document_type": document_type,
            "filename": filename,
            "storage_path": storage_path,
            "mime_type": mime_type,
            "extracted_text": extracted_text,
            "extracted_character_count": extracted_character_count,
        }
        try:
            self.supabase.table("documents").upsert(
                payload,
                on_conflict="interview_id,document_type",
            ).execute()
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Could not upsert document metadata in database",
            ) from exc

    @staticmethod
    def _extract_text_from_pdf(file_bytes: bytes) -> str:
        try:
            pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as exc:
            raise HTTPException(
                status_code=400, detail="Could not read PDF file"
            ) from exc

        pages_text: list[str] = []
        try:
            for page in pdf_document:
                pages_text.append(page.get_text("text"))
        finally:
            pdf_document.close()

        return "\n".join(pages_text).strip()

    def _upload_to_supabase_storage(
        self,
        interview_id: UUID,
        document_type: DocumentType,
        filename: str,
        file_bytes: bytes,
    ) -> str:
        storage_path = f"{interview_id}/{document_type}/{filename}"
        try:
            self.supabase.storage.from_(self.bucket_name).upload(
                path=storage_path,
                file=file_bytes,
                file_options={"content-type": "application/pdf"},
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Could not upload file to Supabase Storage. "
                    "Ensure bucket 'interview-documents' exists."
                ),
            ) from exc

        return storage_path

    def _validate_not_already_uploaded(
        self,
        interview_id: UUID,
        document_type: DocumentType,
        filename: str,
    ) -> None:
        existing_document = (
            self.supabase.table("documents")
            .select("id,filename")
            .eq("interview_id", str(interview_id))
            .eq("document_type", document_type)
            .limit(1)
            .execute()
        )
        existing_data = existing_document.data or []
        if existing_data:
            current_name = (
                existing_data[0].get("filename")
                if isinstance(existing_data[0], dict)
                else None
            )
            detail = f"A {document_type} document is already uploaded" + (
                f": {current_name}" if current_name else ""
            )
            raise HTTPException(status_code=409, detail=detail)

        folder = f"{interview_id}/{document_type}"
        try:
            items = self.supabase.storage.from_(self.bucket_name).list(path=folder)
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Could not validate existing files in Supabase Storage. "
                    "Ensure bucket 'interview-documents' exists."
                ),
            ) from exc

        existing_names = {
            item.get("name")
            for item in (items or [])
            if isinstance(item, dict) and item.get("name")
        }
        if filename in existing_names:
            raise HTTPException(
                status_code=409,
                detail=f"File '{filename}' is already uploaded for {document_type}",
            )

    @staticmethod
    def _normalize_original_filename(filename: str) -> str:
        original_name = PurePath(filename).name.strip()
        if not original_name:
            raise HTTPException(status_code=400, detail="Invalid filename")
        if not original_name.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        return original_name

    @staticmethod
    def _to_snake_case_filename(filename: str) -> str:
        base_name = PurePath(filename).name
        stem = PurePath(base_name).stem.lower()
        stem = re.sub(r"[^a-z0-9]+", "_", stem)
        stem = re.sub(r"_+", "_", stem).strip("_")
        if not stem:
            stem = "document"
        return f"{stem}.pdf"
