export type DocumentType = "resume" | "role_description";

export type DocumentRecord = {
  id: string;
  interview_id: string;
  document_type: DocumentType;
  filename: string;
  storage_path: string;
  mime_type: string | null;
  extracted_text: string | null;
  extracted_character_count: number;
  created_at: string | null;
};

export type DocumentListResponse = {
  interview_id: string;
  documents: DocumentRecord[];
};

export type UploadDocumentResponse = {
  interview_id: string;
  document_type: DocumentType;
  extracted_character_count: number;
  storage_path: string;
};
