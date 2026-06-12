const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function getErrorMessage(
  response: Response,
  fallbackMessage: string
): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string" && payload.detail.trim().length > 0) {
      return payload.detail;
    }
  } catch {
    // ignore JSON parse errors and fall back to default message
  }

  return `${fallbackMessage} (${response.status})`;
}

export type HealthResponse = {
  status: string;
};

export type CreateInterviewRequest = {
  title: string;
  target_questions: number;
  starting_difficulty: number;
};

export type InterviewResponse = {
  id: string;
  status: string;
  title: string | null;
  target_questions: number;
  current_question_number: number;
  current_difficulty: number;
};

export type DocumentType = "resume" | "role_description";

export type UploadDocumentResponse = {
  interview_id: string;
  document_type: DocumentType;
  extracted_character_count: number;
  storage_path: string;
};

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_URL}/health`);

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Health check failed"));
  }

  return response.json() as Promise<HealthResponse>;
}

export async function createInterview(
  payload: CreateInterviewRequest
): Promise<InterviewResponse> {
  const response = await fetch(`${API_URL}/interviews`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Create interview failed"));
  }

  return response.json() as Promise<InterviewResponse>;
}

export async function getInterviews(): Promise<InterviewResponse[]> {
  const response = await fetch(`${API_URL}/interviews`);

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Fetch interviews failed"));
  }

  return response.json() as Promise<InterviewResponse[]>;
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
