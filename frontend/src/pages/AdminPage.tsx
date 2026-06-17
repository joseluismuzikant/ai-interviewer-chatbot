import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { createInterview, getInterviews, deleteInterview } from "../api/interviewsApi";
import { getInterviewDocuments, deleteInterviewDocument } from "../api/documentsApi";
import { InterviewForm } from "../components/interviews/InterviewForm";
import { Card } from "../components/common/Card";
import { PageContainer } from "../components/common/PageContainer";
import { PageTitle } from "../components/common/PageTitle";
import { SectionTitle } from "../components/common/SectionTitle";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { ConfirmDialog } from "../components/common/ConfirmDialog";
import type { InterviewResponse } from "../types/interview";

export function AdminPage() {
  const navigate = useNavigate();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [interviews, setInterviews] = useState<InterviewResponse[]>([]);
  const [listError, setListError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<InterviewResponse | null>(null);

  const fetchInterviews = useCallback(async () => {
    try {
      setListError(null);
      const data = await getInterviews();
      setInterviews(data);
    } catch {
      setListError("Could not load interviews.");
    }
  }, []);

  useEffect(() => {
    fetchInterviews();
  }, [fetchInterviews]);

  async function handleCreate(payload: Parameters<typeof createInterview>[0]) {
    setErrorMessage(null);
    try {
      const interview = await createInterview(payload);
      setInterviews((prev) => [...prev, interview]);
      navigate(`/admin/interviews/${interview.id}`);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Could not create interview"
      );
    }
  }

  async function handleDelete(interview: InterviewResponse) {
    setDeleting(interview.id);
    setErrorMessage(null);
    try {
      const docs = await getInterviewDocuments(interview.id);
      await Promise.all(
        docs.documents.map((d) => deleteInterviewDocument(interview.id, d.filename))
      );
      await deleteInterview(interview.id);
      setInterviews((prev) => prev.filter((i) => i.id !== interview.id));
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Could not delete interview"
      );
    } finally {
      setDeleting(null);
      setConfirmDelete(null);
    }
  }

  return (
    <PageContainer>
      <PageTitle
        title="Admin"
        description="Create interview sessions and move through setup, analysis, interview execution, and final reporting."
      />
      <Card className="workflow-card">
        <SectionTitle title="Workflow" subtitle="MVP interview lifecycle" />
        <ol className="workflow-list">
          <li>Create interview</li>
          <li>Upload resume and role description</li>
          <li>Run match analysis</li>
          <li>Candidate completes interview</li>
          <li>Generate final report</li>
        </ol>
      </Card>

      {listError && <ErrorMessage message={listError} />}

      {interviews.length > 0 && (
        <Card>
          <SectionTitle
            title="Existing Interviews"
            subtitle="Select an interview to continue, or delete one."
          />
          <div className="interview-list">
            {interviews.map((interview) => (
              <div key={interview.id} className="interview-row">
                <div className="interview-row-left">
                  <span className="interview-row-title">
                    {interview.title || "Untitled"}
                  </span>
                  <span className={`status-badge status-${interview.status.toLowerCase()}`}>
                    {interview.status}
                  </span>
                  <span className="interview-row-id">{interview.id}</span>
                </div>
                <div style={{ display: "flex", gap: "0.4rem" }}>
                  <button
                    onClick={() => navigate(`/admin/interviews/${interview.id}`)}
                  >
                    Open
                  </button>
                  <button
                    className="btn-danger"
                    onClick={() => setConfirmDelete(interview)}
                    disabled={deleting === interview.id}
                  >
                    {deleting === interview.id ? "..." : "Delete"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      <Card>
        <SectionTitle
          title="Create Interview"
          subtitle="Start with basic interview metadata."
        />
        <InterviewForm onSubmit={handleCreate} />
        <ErrorMessage message={errorMessage} />
      </Card>

      {confirmDelete && (
        <ConfirmDialog
          title="Delete Interview"
          message={`Are you sure you want to delete "${confirmDelete.title || "Untitled"}"? This will permanently remove all associated documents, messages, and reports.`}
          confirmLabel="Delete"
          cancelLabel="Cancel"
          danger
          loading={deleting === confirmDelete.id}
          onConfirm={() => handleDelete(confirmDelete)}
          onCancel={() => setConfirmDelete(null)}
        />
      )}
    </PageContainer>
  );
}
