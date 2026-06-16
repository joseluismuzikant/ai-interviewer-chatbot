import type { InterviewResponse, MatchAnalysis, StartInterviewResponse } from "../../types/interview";
import type { DocumentListResponse, UploadDocumentResponse } from "../../types/document";
import type { SubmitAnswerResponse } from "../../types/report";

export const FAKE_INTERVIEW_ID = "123e4567-e89b-12d3-a456-426614174000";

export const MOCK_INTERVIEW: InterviewResponse = {
  id: FAKE_INTERVIEW_ID,
  status: "DRAFT",
  title: "Test Interview",
  target_questions: 3,
  current_question_number: 0,
  current_difficulty: 5,
  match_analysis_json: null,
  report_json: null,
};

export const MOCK_ANALYSIS: MatchAnalysis = {
  role_summary: "Senior Engineer role",
  candidate_summary: "Experienced candidate",
  focus_areas: [{ topic: "System Design", reason: "Key requirement" }],
  potential_gaps: [{ topic: "Cloud", reason: "Missing experience" }],
};

export const MOCK_START_RESPONSE: StartInterviewResponse = {
  interview_id: FAKE_INTERVIEW_ID,
  status: "IN_PROGRESS",
  question: {
    id: "q1",
    content: "What is dependency injection?",
    topic: "Design Patterns",
    difficulty: 5,
    question_number: 1,
    expected_signals: ["Inversion of control", "Decoupling"],
  },
};

export const MOCK_DOCUMENTS: DocumentListResponse = {
  interview_id: FAKE_INTERVIEW_ID,
  documents: [
    {
      id: "d1",
      interview_id: FAKE_INTERVIEW_ID,
      document_type: "resume",
      filename: "resume.pdf",
      storage_path: "resume.pdf",
      mime_type: "application/pdf",
      extracted_text: "text",
      extracted_character_count: 100,
      created_at: "2025-01-01T00:00:00Z",
    },
  ],
};

export const MOCK_UPLOAD_RESPONSE: UploadDocumentResponse = {
  interview_id: FAKE_INTERVIEW_ID,
  document_type: "resume",
  extracted_character_count: 100,
  storage_path: "resume.pdf",
};

export const MOCK_SUBMIT_ANSWER_RESPONSE: SubmitAnswerResponse = {
  interview_id: FAKE_INTERVIEW_ID,
  status: "IN_PROGRESS",
  evaluation: {
    score: 8,
    rationale: "Good understanding demonstrated",
    evidence: "Candidate explained DI clearly",
    followup_hint: "Ask about containers",
  },
  next_question: {
    id: "q2",
    content: "How would you implement DI in React?",
    topic: "Design Patterns",
    difficulty: 6,
    question_number: 2,
    expected_signals: ["Context API", "Props"],
  },
};

export const MOCK_FINAL_RESPONSE = {
  summary: "Good candidate",
  overall_score: 7.5,
  strengths: ["Communication", "Technical depth"],
  weaknesses: ["Cloud experience"],
  integrity_notes: [],
  recommendation: "YES" as const,
  recommendation_rationale: "Strong fit for the role",
};

export function mockFetch(responseMap: Record<string, { status?: number; data: unknown }>) {
  return async (url: string, options?: RequestInit) => {
    const method = options?.method || "GET";
    const key = `${method}:${url}`;
    const matched = responseMap[key] || responseMap[url] || { status: 404, data: { detail: "Not found" } };
    return {
      ok: (matched.status || 200) >= 200 && (matched.status || 200) < 300,
      status: matched.status || 200,
      json: async () => matched.data,
    } as Response;
  };
}
