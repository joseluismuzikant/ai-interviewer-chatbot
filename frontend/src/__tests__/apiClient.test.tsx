import { describe, it, expect, vi, beforeEach } from "vitest";
import { API_URL } from "../api/client";
import { createInterview, startInterview } from "../api/interviewsApi";
import { submitAnswer, generateReport } from "../api/reportsApi";
import { FAKE_INTERVIEW_ID, MOCK_INTERVIEW, MOCK_START_RESPONSE } from "../test/mocks/server";

describe("API client", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("uses VITE_API_URL env var", () => {
    expect(API_URL).toBeDefined();
    expect(typeof API_URL).toBe("string");
  });

  it("createInterview calls the correct endpoint", async () => {
    const mock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => MOCK_INTERVIEW,
    } as Response);

    const result = await createInterview({
      title: "Test",
      target_questions: 5,
      starting_difficulty: 5,
    });

    expect(mock).toHaveBeenCalledWith(`${API_URL}/interviews`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: "Test",
        target_questions: 5,
        starting_difficulty: 5,
      }),
    });
    expect(result.id).toBe(FAKE_INTERVIEW_ID);
  });

  it("startInterview calls the correct endpoint", async () => {
    const mock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => MOCK_START_RESPONSE,
    } as Response);

    const result = await startInterview(FAKE_INTERVIEW_ID);

    expect(mock).toHaveBeenCalledWith(
      `${API_URL}/interviews/${FAKE_INTERVIEW_ID}/start`,
      { method: "POST" }
    );
    expect(result.status).toBe("IN_PROGRESS");
  });

  it("submitAnswer calls the correct endpoint with payload", async () => {
    const mock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        interview_id: FAKE_INTERVIEW_ID,
        status: "IN_PROGRESS",
        evaluation: { score: 8, rationale: "r", evidence: "e", followup_hint: "f" },
        next_question: null,
      }),
    } as Response);

    const payload = { answer: "my answer", response_time_ms: 5000, paste_detected: false };
    await submitAnswer(FAKE_INTERVIEW_ID, payload);

    expect(mock).toHaveBeenCalledWith(
      `${API_URL}/interviews/${FAKE_INTERVIEW_ID}/answer`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }
    );
  });

  it("generateReport calls the correct endpoint", async () => {
    const mock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        summary: "s",
        overall_score: 7,
        strengths: [],
        weaknesses: [],
        integrity_notes: [],
        recommendation: "YES" as const,
        recommendation_rationale: "r",
      }),
    } as Response);

    await generateReport(FAKE_INTERVIEW_ID);

    expect(mock).toHaveBeenCalledWith(
      `${API_URL}/interviews/${FAKE_INTERVIEW_ID}/report`,
      { method: "POST" }
    );
  });
});
