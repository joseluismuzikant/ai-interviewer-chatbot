import { FormEvent, useState } from "react";
import type { DocumentType } from "../../types/document";
import type { DocumentRecord } from "../../types/document";

type DocumentUploadProps = {
  documentType: DocumentType;
  label: string;
  existingDocument: DocumentRecord | undefined;
  onUpload: (file: File) => Promise<void>;
  disabled?: boolean;
};

export function DocumentUpload({
  documentType,
  label,
  existingDocument,
  onUpload,
  disabled,
}: DocumentUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setMessage("Please select a PDF file before uploading.");
      return;
    }
    setIsUploading(true);
    setMessage(null);
    try {
      await onUpload(file);
      setMessage(`${documentType} uploaded successfully.`);
      setFile(null);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <form className="upload-card" onSubmit={handleSubmit}>
      <h4>{label}</h4>
      {existingDocument ? (
        <p className="doc-info">
          <strong>{existingDocument.filename}</strong>
          <span>{existingDocument.extracted_character_count} characters extracted</span>
        </p>
      ) : (
        <p className="muted">No {label.toLowerCase()} uploaded yet.</p>
      )}
      <input
        type="file"
        accept="application/pdf,.pdf"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />
      <button type="submit" disabled={isUploading || disabled}>
        {isUploading ? "Uploading..." : `Upload ${label}`}
      </button>
      {message ? <p className={`alert alert-${message.includes("uploaded") ? "success" : "error"}`}>{message}</p> : null}
    </form>
  );
}
