import { API_URL, getErrorMessage } from "./client";
import type { DocumentType, DocumentListResponse, UploadDocumentResponse } from "../types/document";

export async function getInterviewDocuments(
  interviewId: string
): Promise<DocumentListResponse> {
  const response = await fetch(
    `${API_URL}/interviews/${interviewId}/documents`
  );
  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Fetch documents failed"));
  }
  return response.json() as Promise<DocumentListResponse>;
}

export async function uploadInterviewDocument(
  interviewId: string,
  documentType: DocumentType,
  file: File
): Promise<UploadDocumentResponse> {
  const formData = new FormData();
  formData.append("document_type", documentType);
  formData.append("file", file);

  const response = await fetch(`${API_URL}/interviews/${interviewId}/documents`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Upload failed"));
  }

  return response.json() as Promise<UploadDocumentResponse>;
}
