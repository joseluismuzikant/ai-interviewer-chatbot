import { apiFetch } from "./client";
import type { CreateInterviewRequest, InterviewResponse, MatchAnalysis, StartInterviewResponse } from "../types/interview";
import type { MessageResponse } from "../types/message";

export function createInterview(payload: CreateInterviewRequest): Promise<InterviewResponse> {
  return apiFetch<InterviewResponse>("/interviews", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function getInterviews(): Promise<InterviewResponse[]> {
  return apiFetch<InterviewResponse[]>("/interviews");
}

export function getInterview(interviewId: string): Promise<InterviewResponse> {
  return apiFetch<InterviewResponse>(`/interviews/${interviewId}`);
}

export function analyzeInterview(interviewId: string): Promise<MatchAnalysis> {
  return apiFetch<MatchAnalysis>(`/interviews/${interviewId}/analyze`, { method: "POST" });
}

export function startInterview(interviewId: string): Promise<StartInterviewResponse> {
  return apiFetch<StartInterviewResponse>(`/interviews/${interviewId}/start`, { method: "POST" });
}

export function getInterviewMessages(interviewId: string): Promise<MessageResponse[]> {
  return apiFetch<MessageResponse[]>(`/interviews/${interviewId}/messages`);
}
