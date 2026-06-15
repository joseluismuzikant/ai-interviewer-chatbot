import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useParams } from "react-router-dom";

import {
  InterviewResponse,
  StartQuestion,
  getInterview,
  getInterviewMessages,
  startInterview,
  submitAnswer,
} from "../api/client";

const UUID_REGEX =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export function CandidateInterviewPage() {
  const { id } = useParams();
  const interviewId = id?.trim() ?? "";
  const hasInterviewId = interviewId.length > 0;
  const hasValidInterviewId = UUID_REGEX.test(interviewId);

  const [interview, setInterview] = useState<InterviewResponse | null>(null);
  const [question, setQuestion] = useState<StartQuestion | null>(null);
  const [answerText, setAnswerText] = useState("");
  const [pasteDetected, setPasteDetected] = useState(false);
  const [questionShownAt, setQuestionShownAt] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    async function loadInterview() {
      if (!hasInterviewId) {
        setInterview(null);
        setQuestion(null);
        setErrorMessage(null);
        setIsLoading(false);
        return;
      }

      if (!hasValidInterviewId) {
        setInterview(null);
        setQuestion(null);
        setErrorMessage(
          "Invalid interview ID format. Select a real interview from Admin."
        );
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setErrorMessage(null);

      try {
        const loadedInterview = await getInterview(interviewId);
        setInterview(loadedInterview);

        if (loadedInterview.status === "IN_PROGRESS") {
          try {
            const started = await startInterview(interviewId);
            setQuestion(started.question);
          } catch {
            const messages = await getInterviewMessages(interviewId);
            const latestAssistant = [...messages]
              .reverse()
              .find((message) => message.role === "assistant");
            if (latestAssistant) {
              setQuestion({
                id: latestAssistant.id,
                content: latestAssistant.content,
                topic: "Unknown topic",
                difficulty: latestAssistant.difficulty_level ?? 0,
                question_number: latestAssistant.question_number ?? 1,
                expected_signals: [],
              });
            }
          }
        }
      } catch (error) {
        setErrorMessage(
          error instanceof Error ? error.message : "Could not load interview"
        );
      } finally {
        setIsLoading(false);
      }
    }

    void loadInterview();
  }, [hasInterviewId, hasValidInterviewId, interviewId]);

  async function handleStartInterview() {
    if (!hasValidInterviewId) {
      return;
    }

    setIsStarting(true);
    setErrorMessage(null);

    try {
      const started = await startInterview(interviewId);
      setQuestion(started.question);
      setAnswerText("");
      setPasteDetected(false);
      setInterview((previous) =>
        previous
          ? { ...previous, status: started.status, current_question_number: 1 }
          : previous
      );
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Could not start interview"
      );
    } finally {
      setIsStarting(false);
    }
  }

  useEffect(() => {
    if (question) {
      setQuestionShownAt(Date.now());
      setAnswerText("");
      setPasteDetected(false);
    }
  }, [question?.id, question?.question_number, question?.content]);

  async function handleSubmitAnswer() {
    if (!hasValidInterviewId || !question) {
      return;
    }
    const trimmed = answerText.trim();
    if (!trimmed) {
      setErrorMessage("Answer cannot be empty.");
      return;
    }

    const responseTime = questionShownAt ? Date.now() - questionShownAt : 0;

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      const response = await submitAnswer(interviewId, {
        answer: trimmed,
        response_time_ms: responseTime,
        paste_detected: pasteDetected,
      });

      if (response.status === "COMPLETED") {
        setInterview((previous) =>
          previous ? { ...previous, status: "COMPLETED" } : previous
        );
        setQuestion(null);
      } else {
        setInterview((previous) =>
          previous
            ? {
                ...previous,
                status: "IN_PROGRESS",
                current_question_number: response.next_question?.question_number ??
                  previous.current_question_number,
              }
            : previous
        );
        setQuestion(response.next_question);
      }
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Could not submit answer"
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section>
      <h2>Candidate Interview</h2>

      {!hasInterviewId ? (
        <p>
          No interview selected. Go to <Link to="/admin/interviews">Interview Details</Link> and open the candidate interview from a real interview.
        </p>
      ) : null}

      {hasInterviewId && !hasValidInterviewId ? (
        <p>
          The URL interview ID is invalid. Use <Link to="/admin/interviews">Interview Details</Link> to choose a valid interview.
        </p>
      ) : null}

      {isLoading ? <p>Loading interview...</p> : null}
      {errorMessage ? <p className="form-error">{errorMessage}</p> : null}

      <p>Interview ID: {id ?? "(none)"}</p>
      <p>Status: {interview?.status ?? "Unknown"}</p>

      {question && interview?.target_questions ? (
        <p>
          Question {question.question_number} of {interview.target_questions}
        </p>
      ) : null}

      {interview?.status === "READY" ? (
        <button
          type="button"
          onClick={handleStartInterview}
          disabled={isStarting}
        >
          {isStarting ? "Starting..." : "Start Interview"}
        </button>
      ) : null}

      {interview?.status === "COMPLETED" ? (
        <p>Interview completed. Thank you for your responses.</p>
      ) : null}

      {question ? (
        <div className="analysis-result">
          <h3>Current Question</h3>
          <div className="analysis-block">
            <strong>Question</strong>
            <p>{question.content}</p>
          </div>
          <div className="analysis-block">
            <strong>Topic</strong>
            <p>{question.topic}</p>
          </div>
          <div className="analysis-block">
            <strong>Difficulty</strong>
            <p>{question.difficulty}</p>
          </div>
          {interview?.status !== "COMPLETED" ? (
            <div className="analysis-block">
              <strong>Your Answer</strong>
              <textarea
                value={answerText}
                onChange={(event) => setAnswerText(event.target.value)}
                onPaste={() => setPasteDetected(true)}
                rows={6}
                placeholder="Type your answer here..."
                disabled={isSubmitting}
              />
              <button
                type="button"
                onClick={handleSubmitAnswer}
                disabled={isSubmitting}
              >
                {isSubmitting
                  ? "Evaluating answer and preparing next question..."
                  : "Submit Answer"}
              </button>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
