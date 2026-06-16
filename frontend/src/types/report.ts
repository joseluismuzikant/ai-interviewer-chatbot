export type AnswerEvaluation = {
  score: number;
  rationale: string;
  evidence: string;
  followup_hint: string;
};

export type SubmitAnswerRequest = {
  answer: string;
  response_time_ms: number;
  paste_detected: boolean;
};

export type SubmitAnswerResponse = {
  interview_id: string;
  status: "IN_PROGRESS" | "COMPLETED";
  evaluation: AnswerEvaluation;
  next_question: {
    id?: string;
    content: string;
    topic: string;
    difficulty: number;
    question_number: number;
    expected_signals: string[];
  } | null;
};
