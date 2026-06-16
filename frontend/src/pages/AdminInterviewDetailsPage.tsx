import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  getInterviews,
  getInterview,
  analyzeInterview,
  getInterviewMessages,
} from "../api/interviewsApi";
import { getInterviewDocuments, uploadInterviewDocument } from "../api/documentsApi";
import { generateReport, getReport } from "../api/reportsApi";
import type { InterviewResponse, MatchAnalysis } from "../types/interview";
import type { DocumentRecord, DocumentType } from "../types/document";
import type { MessageResponse } from "../types/message";
import type { FinalReportResponse } from "../types/interview";
import { PageContainer } from "../components/common/PageContainer";
import { PageTitle } from "../components/common/PageTitle";
import { SectionTitle } from "../components/common/SectionTitle";
import { Card } from "../components/common/Card";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingState } from "../components/common/LoadingState";
import { EmptyState } from "../components/common/EmptyState";
import { InterviewPicker } from "../components/interviews/InterviewPicker";
import { DocumentUpload } from "../components/documents/DocumentUpload";
import { ReportView } from "../components/reports/ReportView";
import { StatusBadge } from "../components/common/StatusBadge";
import { MessageBubble } from "../components/chat/MessageBubble";

export function AdminInterviewDetailsPage() {
  const { id } = useParams();
  const [interviews, setInterviews] = useState<InterviewResponse[]>([]);
  const [selectedInterviewId, setSelectedInterviewId] = useState("");
  const [selectedInterview, setSelectedInterview] = useState<InterviewResponse | null>(null);
  const [isLoadingInterviews, setIsLoadingInterviews] = useState(true);
  const [interviewsError, setInterviewsError] = useState<string | null>(null);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<MatchAnalysis | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [reportResult, setReportResult] = useState<FinalReportResponse | null>(null);
  const [reportError, setReportError] = useState<string | null>(null);

  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [messagesError, setMessagesError] = useState<string | null>(null);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);

  const resumeDocument = useMemo(
    () => documents.find((d) => d.document_type === "resume"),
    [documents]
  );
  const roleDocument = useMemo(
    () => documents.find((d) => d.document_type === "role_description"),
    [documents]
  );

  useEffect(() => {
    let mounted = true;
    async function load() {
      setIsLoadingInterviews(true);
      setInterviewsError(null);
      try {
        const data = await getInterviews();
        if (!mounted) return;
        setInterviews(data);
        if (data.length === 0) {
          setSelectedInterviewId("");
          return;
        }
        const hasParamId = Boolean(id) && data.some((item) => item.id === id);
        setSelectedInterviewId(hasParamId ? (id as string) : data[0].id);
      } catch (error) {
        if (!mounted) return;
        setInterviewsError(error instanceof Error ? error.message : "Could not load interviews");
      } finally {
        if (mounted) setIsLoadingInterviews(false);
      }
    }
    void load();
    return () => { mounted = false; };
  }, [id]);

  async function loadDocuments(interviewId: string) {
    try {
      const data = await getInterviewDocuments(interviewId);
      setDocuments(data.documents);
    } catch {
      setDocuments([]);
    }
  }

  async function loadInterviewDetails(interviewId: string) {
    try {
      const interview = await getInterview(interviewId);
      setSelectedInterview(interview);
      setAnalysisResult(interview.match_analysis_json ?? null);
      if (interview.report_json) {
        setReportResult(interview.report_json);
        setReportError(null);
        return;
      }
      if (interview.status === "COMPLETED") {
        try {
          const report = await getReport(interviewId);
          setReportResult(report);
          setReportError(null);
        } catch {
          setReportResult(null);
        }
      } else {
        setReportResult(null);
        setReportError(null);
      }
    } catch (error) {
      setSelectedInterview(null);
      setReportResult(null);
      setAnalysisResult(null);
      setInterviewsError(error instanceof Error ? error.message : "Could not load interview details");
    }
  }

  async function loadMessages(interviewId: string) {
    setIsLoadingMessages(true);
    setMessagesError(null);
    try {
      const data = await getInterviewMessages(interviewId);
      setMessages(data);
    } catch (error) {
      setMessages([]);
      setMessagesError(error instanceof Error ? error.message : "Could not load transcript");
    } finally {
      setIsLoadingMessages(false);
    }
  }

  useEffect(() => {
    if (!selectedInterviewId) {
      setDocuments([]);
      setSelectedInterview(null);
      setAnalysisResult(null);
      setReportResult(null);
      setMessages([]);
      return;
    }
    void loadDocuments(selectedInterviewId);
    void loadInterviewDetails(selectedInterviewId);
    void loadMessages(selectedInterviewId);
  }, [selectedInterviewId]);

  async function handleUpload(documentType: DocumentType, file: File) {
    await uploadInterviewDocument(selectedInterviewId, documentType, file);
    void loadDocuments(selectedInterviewId);
  }

  async function handleAnalyze() {
    if (!selectedInterviewId) return;
    setIsAnalyzing(true);
    setAnalysisResult(null);
    setAnalysisError(null);
    try {
      const result = await analyzeInterview(selectedInterviewId);
      setAnalysisResult(result);
      setSelectedInterview((prev) =>
        prev ? { ...prev, status: "READY", match_analysis_json: result } : prev
      );
      setInterviews((prev) =>
        prev.map((item) =>
          item.id === selectedInterviewId
            ? { ...item, status: "READY", match_analysis_json: result }
            : item
        )
      );
    } catch (error) {
      setAnalysisError(error instanceof Error ? error.message : "Analysis failed");
    } finally {
      setIsAnalyzing(false);
    }
  }

  async function handleGenerateReport() {
    if (!selectedInterviewId) return;
    setIsGeneratingReport(true);
    setReportError(null);
    try {
      const report = await generateReport(selectedInterviewId);
      setReportResult(report);
      setSelectedInterview((prev) => (prev ? { ...prev, report_json: report } : prev));
      setInterviews((prev) =>
        prev.map((item) =>
          item.id === selectedInterviewId ? { ...item, report_json: report } : item
        )
      );
      void loadMessages(selectedInterviewId);
    } catch (error) {
      setReportError(error instanceof Error ? error.message : "Could not generate report");
    } finally {
      setIsGeneratingReport(false);
    }
  }

  return (
    <PageContainer>
      <PageTitle
        title="Interview Details"
        description="Set up interview inputs, review AI analysis, and inspect final outcomes."
      />
      <ErrorMessage message={interviewsError} />

      <Card>
        <SectionTitle title="Setup" subtitle="Select an interview and open the candidate view." />
        <InterviewPicker
          interviews={interviews}
          selectedId={selectedInterviewId}
          onChange={setSelectedInterviewId}
          disabled={isLoadingInterviews}
        />
        {isLoadingInterviews ? <LoadingState message="Loading interviews..." /> : null}

        {selectedInterviewId ? (
          <div className="setup-meta-grid">
            <div className="setup-meta-item">
              <span className="meta-label">Status</span>
              <StatusBadge status={selectedInterview?.status} />
            </div>
            <div className="setup-meta-item">
              <span className="meta-label">Interview ID</span>
              <code className="inline-id">{selectedInterviewId}</code>
            </div>
            <div className="setup-meta-item">
              <span className="meta-label">Candidate Link</span>
              <Link className="text-link" to={`/interview/${selectedInterviewId}`}>
                Open Candidate Interview View
              </Link>
            </div>
          </div>
        ) : null}
      </Card>

      <Card>
        <SectionTitle
          title="Documents"
          subtitle="Upload one resume and one role description PDF. Re-uploads replace previous files."
        />
        <div className="upload-grid">
          <DocumentUpload
            documentType="resume"
            label="Resume"
            existingDocument={resumeDocument}
            onUpload={(file) => handleUpload("resume", file)}
            disabled={!selectedInterviewId}
          />
          <DocumentUpload
            documentType="role_description"
            label="Role Description"
            existingDocument={roleDocument}
            onUpload={(file) => handleUpload("role_description", file)}
            disabled={!selectedInterviewId}
          />
        </div>
      </Card>

      <Card>
        <SectionTitle
          title="Match Analysis"
          subtitle="Generate candidate-role fit insights from uploaded documents."
          actions={
            <button type="button" onClick={handleAnalyze} disabled={isAnalyzing || !selectedInterviewId}>
              {isAnalyzing ? "Analyzing..." : "Run Match Analysis"}
            </button>
          }
        />
        <ErrorMessage message={analysisError} />
        {analysisResult ? (
          <div className="analysis-layout">
            <div className="summary-grid">
              <Card className="summary-card">
                <h4>Role Summary</h4>
                <p>{analysisResult.role_summary}</p>
              </Card>
              <Card className="summary-card">
                <h4>Candidate Summary</h4>
                <p>{analysisResult.candidate_summary}</p>
              </Card>
            </div>
            <div className="analysis-columns">
              <div>
                <h4>Focus Areas</h4>
                {analysisResult.focus_areas.length === 0 ? (
                  <p className="muted">None identified.</p>
                ) : (
                  <div className="chip-grid">
                    {analysisResult.focus_areas.map((item, idx) => (
                      <Card key={`fa-${idx}`} className="chip-card">
                        <strong>{item.topic}</strong>
                        <p>{item.reason}</p>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
              <div>
                <h4>Potential Gaps</h4>
                {analysisResult.potential_gaps.length === 0 ? (
                  <p className="muted">None identified.</p>
                ) : (
                  <div className="chip-grid">
                    {analysisResult.potential_gaps.map((item, idx) => (
                      <Card key={`pg-${idx}`} className="chip-card">
                        <strong>{item.topic}</strong>
                        <p>{item.reason}</p>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <EmptyState message="Run analysis to display structured candidate-role insights." />
        )}
      </Card>

      <Card>
        <SectionTitle
          title="Final Report"
          subtitle="Generate final interview recommendation after completion."
          actions={
            selectedInterview?.status === "COMPLETED" ? (
              <button
                type="button"
                onClick={handleGenerateReport}
                disabled={isGeneratingReport || !selectedInterviewId}
              >
                {isGeneratingReport ? "Generating report..." : "Generate Report"}
              </button>
            ) : null
          }
        />
        {selectedInterview?.status !== "COMPLETED" ? (
          <p className="alert alert-info">
            Final report is available when the interview status is COMPLETED.
          </p>
        ) : null}
        <ErrorMessage message={reportError} />
        {reportResult ? (
          <ReportView report={reportResult} status={selectedInterview?.status} />
        ) : selectedInterview?.status === "COMPLETED" ? (
          <EmptyState message="No final report generated yet." />
        ) : null}
      </Card>

      <Card>
        <SectionTitle title="Transcript" subtitle="Ordered interview conversation and candidate responses." />
        <ErrorMessage message={messagesError} />
        {isLoadingMessages ? <LoadingState message="Loading transcript..." /> : null}

        {!isLoadingMessages && messages.length === 0 ? (
          <EmptyState message="No messages yet." />
        ) : (
          <div className="chat-thread">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
          </div>
        )}
      </Card>
    </PageContainer>
  );
}
