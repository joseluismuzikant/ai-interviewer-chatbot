const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

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

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_URL}/health`);

  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
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
    throw new Error(`Create interview failed: ${response.status}`);
  }

  return response.json() as Promise<InterviewResponse>;
}
