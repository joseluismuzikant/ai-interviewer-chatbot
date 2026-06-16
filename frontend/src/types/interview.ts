export type InterviewResponse = {
  id: string;
  status: string;
  title: string | null;
  target_questions: number;
  current_question_number: number;
  current_difficulty: number;
  match_analysis_json?: MatchAnalysis | null;
  report_json?: FinalReportResponse | null;
};

export type CreateInterviewRequest = {
  title: string;
  target_questions: number;
  starting_difficulty: number;
};

export type AnalysisItem = {
  topic: string;
  reason: string;
};

export type MatchAnalysis = {
  role_summary: string;
  candidate_summary: string;
  focus_areas: AnalysisItem[];
  potential_gaps: AnalysisItem[];
};

export type StartQuestion = {
  id?: string;
  content: string;
  topic: string;
  difficulty: number;
  question_number: number;
  expected_signals: string[];
};

export type StartInterviewResponse = {
  interview_id: string;
  status: "IN_PROGRESS";
  question: StartQuestion;
};

export type FinalReportResponse = {
  summary: string;
  overall_score: number;
  strengths: string[];
  weaknesses: string[];
  integrity_notes: string[];
  recommendation: "YES" | "MIXED" | "NO";
  recommendation_rationale: string;
};
