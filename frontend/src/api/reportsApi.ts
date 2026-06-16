import { apiFetch } from "./client";
import type { SubmitAnswerRequest, SubmitAnswerResponse } from "../types/report";
import type { FinalReportResponse } from "../types/interview";

export function submitAnswer(
  interviewId: string,
  payload: SubmitAnswerRequest
): Promise<SubmitAnswerResponse> {
  return apiFetch<SubmitAnswerResponse>(`/interviews/${interviewId}/answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function generateReport(interviewId: string): Promise<FinalReportResponse> {
  return apiFetch<FinalReportResponse>(`/interviews/${interviewId}/report`, {
    method: "POST",
  });
}

export function getReport(interviewId: string): Promise<FinalReportResponse> {
  return apiFetch<FinalReportResponse>(`/interviews/${interviewId}/report`);
}
