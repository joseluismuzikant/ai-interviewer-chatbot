import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getInterview, startInterview, getInterviewMessages } from "../api/interviewsApi";
import { submitAnswer } from "../api/reportsApi";
import type { InterviewResponse, StartQuestion } from "../types/interview";
import type { AnswerEvaluation } from "../types/report";
import { PageContainer } from "../components/common/PageContainer";
import { PageTitle } from "../components/common/PageTitle";
import { SectionTitle } from "../components/common/SectionTitle";
import { Card } from "../components/common/Card";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingState } from "../components/common/LoadingState";
import { StatusBadge } from "../components/common/StatusBadge";
import { ChatWindow } from "../components/chat/ChatWindow";

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
  const [evaluation, setEvaluation] = useState<AnswerEvaluation | null>(null);

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
        setErrorMessage("Invalid interview ID format. Select a real interview from Admin.");
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
              .find((m) => m.role === "assistant");
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
    if (!hasValidInterviewId) return;
    setIsStarting(true);
    setErrorMessage(null);
    try {
      const started = await startInterview(interviewId);
      setQuestion(started.question);
      setAnswerText("");
      setPasteDetected(false);
      setInterview((prev) =>
        prev ? { ...prev, status: started.status, current_question_number: 1 } : prev
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
      setEvaluation(null);
    }
  }, [question?.id, question?.question_number, question?.content]);

  async function handleSubmitAnswer() {
    if (!hasValidInterviewId || !question) return;
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
      setEvaluation(response.evaluation);
      if (response.status === "COMPLETED") {
        setInterview((prev) => (prev ? { ...prev, status: "COMPLETED" } : prev));
        setQuestion(null);
      } else {
        setInterview((prev) =>
          prev
            ? {
                ...prev,
                status: "IN_PROGRESS",
                current_question_number:
                  response.next_question?.question_number ?? prev.current_question_number,
              }
            : prev
        );
        setQuestion(response.next_question);
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Could not submit answer");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <PageContainer>
      <PageTitle
        title="Candidate Interview"
        description="Answer each question clearly. Your responses are evaluated to generate a final interview report."
      />

      {!hasInterviewId ? (
        <p className="alert alert-info">
          No interview selected. Go to <Link to="/admin/interviews">Interview Details</Link> and open a
          candidate interview from a real interview.
        </p>
      ) : null}

      {hasInterviewId && !hasValidInterviewId ? (
        <p className="alert alert-error">
          The URL interview ID is invalid. Use <Link to="/admin/interviews">Interview Details</Link> to
          choose a valid interview.
        </p>
      ) : null}

      <ErrorMessage message={errorMessage} />

      <Card>
        <SectionTitle title="Interview Session" subtitle="Current interview state" />
        {isLoading ? <LoadingState message="Loading interview..." /> : null}

        <div className="setup-meta-grid">
          <div className="setup-meta-item">
            <span className="meta-label">Interview ID</span>
            <code className="inline-id">{id ?? "(none)"}</code>
          </div>
          <div className="setup-meta-item">
            <span className="meta-label">Status</span>
            <StatusBadge status={interview?.status} />
          </div>
          {question && interview?.target_questions ? (
            <div className="setup-meta-item">
              <span className="meta-label">Progress</span>
              <strong>
                Question {question.question_number} of {interview.target_questions}
              </strong>
            </div>
          ) : null}
        </div>

        {interview?.status === "READY" ? (
          <button type="button" onClick={handleStartInterview} disabled={isStarting}>
            {isStarting ? "Starting..." : "Start Interview"}
          </button>
        ) : null}
      </Card>

      {interview?.status === "COMPLETED" ? (
        <Card className="completion-card">
          <h3>Interview completed. Thank you for your responses.</h3>
        </Card>
      ) : null}

      {question || evaluation ? (
        <ChatWindow
          messages={[]}
          question={question}
          answerText={answerText}
          onAnswerChange={setAnswerText}
          onPasteDetected={() => setPasteDetected(true)}
          onSubmitAnswer={handleSubmitAnswer}
          isSubmitting={isSubmitting}
          isCompleted={interview?.status === "COMPLETED"}
          evaluation={evaluation}
        />
      ) : null}
    </PageContainer>
  );
}
