export type MessageResponse = {
  id: string;
  interview_id: string;
  role: "assistant" | "candidate" | "system";
  content: string;
  question_number: number | null;
  difficulty_level: number | null;
  answer_quality_score: number | null;
  response_time_ms: number | null;
  paste_detected: boolean | null;
  created_at: string | null;
};
