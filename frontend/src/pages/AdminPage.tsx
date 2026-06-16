import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createInterview } from "../api/interviewsApi";
import { InterviewForm } from "../components/interviews/InterviewForm";
import { Card } from "../components/common/Card";
import { PageContainer } from "../components/common/PageContainer";
import { PageTitle } from "../components/common/PageTitle";
import { SectionTitle } from "../components/common/SectionTitle";
import { ErrorMessage } from "../components/common/ErrorMessage";

export function AdminPage() {
  const navigate = useNavigate();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleCreate(payload: Parameters<typeof createInterview>[0]) {
    setErrorMessage(null);
    try {
      const interview = await createInterview(payload);
      navigate(`/admin/interviews/${interview.id}`);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Could not create interview"
      );
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
      <Card>
        <SectionTitle
          title="Create Interview"
          subtitle="Start with basic interview metadata."
        />
        <InterviewForm onSubmit={handleCreate} />
        <ErrorMessage message={errorMessage} />
      </Card>
    </PageContainer>
  );
}
