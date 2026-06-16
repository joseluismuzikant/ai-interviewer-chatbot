import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  DocumentRecord,
  DocumentType,
  FinalReportResponse,
  InterviewResponse,
  MatchAnalysis,
  MessageResponse,
  UploadDocumentResponse,
  analyzeInterview,
  generateReport,
  getInterview,
  getInterviewDocuments,
  getInterviewMessages,
  getInterviews,
  getReport,
  uploadInterviewDocument,
} from "../api/client";
import {
  AlertMessage,
  Card,
  MetricCard,
  PageContainer,
  PageTitle,
  SectionTitle,
  StatusBadge,
} from "../components/ui";

type UploadState = {
  isUploading: boolean;
  message: string | null;
};

function formatDate(value: string | null): string {
  if (!value) {
    return "";
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return "";
  }

  return parsed.toLocaleString();
}

function shortId(id: string): string {
  if (id.length <= 16) {
    return id;
  }
  return `${id.slice(0, 8)}...${id.slice(-6)}`;
}

export function AdminInterviewDetailsPage() {
  const { id } = useParams();
  const [interviews, setInterviews] = useState<InterviewResponse[]>([]);
  const [selectedInterviewId, setSelectedInterviewId] = useState("");
  const [selectedInterview, setSelectedInterview] = useState<InterviewResponse | null>(
    null
  );
  const [isLoadingInterviews, setIsLoadingInterviews] = useState(true);
  const [interviewsError, setInterviewsError] = useState<string | null>(null);

  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [roleFile, setRoleFile] = useState<File | null>(null);
  const [resumeState, setResumeState] = useState<UploadState>({
    isUploading: false,
    message: null,
  });
  const [roleState, setRoleState] = useState<UploadState>({
    isUploading: false,
    message: null,
  });

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
    () => documents.find((item) => item.document_type === "resume"),
    [documents]
  );
  const roleDocument = useMemo(
    () => documents.find((item) => item.document_type === "role_description"),
    [documents]
  );

  useEffect(() => {
    let isMounted = true;

    async function loadInterviews() {
      setIsLoadingInterviews(true);
      setInterviewsError(null);

      try {
        const data = await getInterviews();
        if (!isMounted) {
          return;
        }

        setInterviews(data);
        if (data.length === 0) {
          setSelectedInterviewId("");
          return;
        }

        const hasParamId = Boolean(id) && data.some((item) => item.id === id);
        setSelectedInterviewId(hasParamId ? (id as string) : data[0].id);
      } catch (error) {
        if (!isMounted) {
          return;
        }
        setInterviewsError(
          error instanceof Error ? error.message : "Could not load interviews"
        );
      } finally {
        if (isMounted) {
          setIsLoadingInterviews(false);
        }
      }
    }

    void loadInterviews();

    return () => {
      isMounted = false;
    };
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
      setInterviewsError(
        error instanceof Error
          ? error.message
          : "Could not load interview details"
      );
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
      setMessagesError(
        error instanceof Error ? error.message : "Could not load transcript"
      );
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

  async function submitUpload(
    event: FormEvent<HTMLFormElement>,
    documentType: DocumentType
  ) {
    event.preventDefault();
    if (!selectedInterviewId) {
      return;
    }

    const selectedFile = documentType === "resume" ? resumeFile : roleFile;
    if (!selectedFile) {
      const noFileMessage = "Please select a PDF file before uploading.";
      if (documentType === "resume") {
        setResumeState({ isUploading: false, message: noFileMessage });
      } else {
        setRoleState({ isUploading: false, message: noFileMessage });
      }
      return;
    }

    const setState = documentType === "resume" ? setResumeState : setRoleState;
    setState({ isUploading: true, message: null });

    try {
      const result: UploadDocumentResponse = await uploadInterviewDocument(
        selectedInterviewId,
        documentType,
        selectedFile
      );
      setState({
        isUploading: false,
        message: `${documentType} uploaded (${result.extracted_character_count} chars extracted).`,
      });
      void loadDocuments(selectedInterviewId);
    } catch (error) {
      setState({
        isUploading: false,
        message: error instanceof Error ? error.message : "Upload failed",
      });
    }
  }

  async function handleAnalyze() {
    if (!selectedInterviewId) {
      return;
    }

    setIsAnalyzing(true);
    setAnalysisResult(null);
    setAnalysisError(null);

    try {
      const result = await analyzeInterview(selectedInterviewId);
      setAnalysisResult(result);
      setSelectedInterview((previous) =>
        previous
          ? {
              ...previous,
              status: "READY",
              match_analysis_json: result,
            }
          : previous
      );
      setInterviews((previous) =>
        previous.map((item) =>
          item.id === selectedInterviewId
            ? {
                ...item,
                status: "READY",
                match_analysis_json: result,
              }
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
    if (!selectedInterviewId) {
      return;
    }

    setIsGeneratingReport(true);
    setReportError(null);

    try {
      const report = await generateReport(selectedInterviewId);
      setReportResult(report);
      setSelectedInterview((previous) =>
        previous
          ? {
              ...previous,
              report_json: report,
            }
          : previous
      );
      setInterviews((previous) =>
        previous.map((item) =>
          item.id === selectedInterviewId
            ? {
                ...item,
                report_json: report,
              }
            : item
        )
      );
      void loadMessages(selectedInterviewId);
    } catch (error) {
      setReportError(
        error instanceof Error ? error.message : "Could not generate report"
      );
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

      {interviewsError ? <AlertMessage kind="error">{interviewsError}</AlertMessage> : null}

      <Card>
        <SectionTitle title="Setup" subtitle="Select an interview and open the candidate view." />

        <label className="interview-picker">
          Interview
          <select
            value={selectedInterviewId}
            onChange={(event) => setSelectedInterviewId(event.target.value)}
            disabled={isLoadingInterviews || interviews.length === 0}
          >
            {interviews.length === 0 ? (
              <option value="">No interviews available</option>
            ) : (
              interviews.map((interview) => (
                <option key={interview.id} value={interview.id}>
                  {interview.title?.trim() || `Untitled interview (${shortId(interview.id)})`}
                </option>
              ))
            )}
          </select>
        </label>

        {isLoadingInterviews ? <p className="muted">Loading interviews...</p> : null}

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
          <form className="upload-card" onSubmit={(event) => submitUpload(event, "resume")}>
            <h4>Resume</h4>
            {resumeDocument ? (
              <p className="doc-info">
                <strong>{resumeDocument.filename}</strong>
                <span>{resumeDocument.extracted_character_count} characters extracted</span>
              </p>
            ) : (
              <p className="muted">No resume uploaded yet.</p>
            )}

            <input
              type="file"
              accept="application/pdf,.pdf"
              onChange={(event) => setResumeFile(event.target.files?.[0] ?? null)}
            />
            <button type="submit" disabled={resumeState.isUploading || !selectedInterviewId}>
              {resumeState.isUploading ? "Uploading..." : "Upload Resume"}
            </button>
            {resumeState.message ? <AlertMessage kind="info">{resumeState.message}</AlertMessage> : null}
          </form>

          <form
            className="upload-card"
            onSubmit={(event) => submitUpload(event, "role_description")}
          >
            <h4>Role Description</h4>
            {roleDocument ? (
              <p className="doc-info">
                <strong>{roleDocument.filename}</strong>
                <span>{roleDocument.extracted_character_count} characters extracted</span>
              </p>
            ) : (
              <p className="muted">No role description uploaded yet.</p>
            )}

            <input
              type="file"
              accept="application/pdf,.pdf"
              onChange={(event) => setRoleFile(event.target.files?.[0] ?? null)}
            />
            <button type="submit" disabled={roleState.isUploading || !selectedInterviewId}>
              {roleState.isUploading ? "Uploading..." : "Upload Role Description"}
            </button>
            {roleState.message ? <AlertMessage kind="info">{roleState.message}</AlertMessage> : null}
          </form>
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

        {analysisError ? <AlertMessage kind="error">{analysisError}</AlertMessage> : null}

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
                      <Card key={`${item.topic}-${idx}`} className="chip-card">
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
                      <Card key={`${item.topic}-${idx}`} className="chip-card">
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
          <p className="muted">Run analysis to display structured candidate-role insights.</p>
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
          <AlertMessage kind="info">
            Final report is available when the interview status is COMPLETED.
          </AlertMessage>
        ) : null}

        {reportError ? <AlertMessage kind="error">{reportError}</AlertMessage> : null}

        {reportResult ? (
          <div className="report-layout">
            <div className="report-metrics">
              <MetricCard label="Overall Score" value={reportResult.overall_score} tone="accent" />
              <div className="metric-card metric-neutral">
                <span className="metric-label">Recommendation</span>
                <strong
                  className={`recommendation-badge recommendation-${reportResult.recommendation.toLowerCase()}`}
                >
                  {reportResult.recommendation}
                </strong>
              </div>
            </div>

            <Card className="summary-card">
              <h4>Summary</h4>
              <p>{reportResult.summary}</p>
            </Card>

            <div className="report-columns">
              <Card>
                <h4>Strengths</h4>
                {reportResult.strengths.length === 0 ? (
                  <p className="muted">No strengths listed.</p>
                ) : (
                  <ul>
                    {reportResult.strengths.map((item, idx) => (
                      <li key={`${item}-${idx}`}>{item}</li>
                    ))}
                  </ul>
                )}
              </Card>

              <Card>
                <h4>Weaknesses</h4>
                {reportResult.weaknesses.length === 0 ? (
                  <p className="muted">No weaknesses listed.</p>
                ) : (
                  <ul>
                    {reportResult.weaknesses.map((item, idx) => (
                      <li key={`${item}-${idx}`}>{item}</li>
                    ))}
                  </ul>
                )}
              </Card>
            </div>

            <Card>
              <h4>Recommendation Rationale</h4>
              <p>{reportResult.recommendation_rationale}</p>
            </Card>

            {reportResult.integrity_notes.length > 0 ? (
              <Card>
                <h4>Integrity Notes</h4>
                <ul>
                  {reportResult.integrity_notes.map((item, idx) => (
                    <li key={`${item}-${idx}`}>{item}</li>
                  ))}
                </ul>
              </Card>
            ) : null}
          </div>
        ) : (
          <p className="muted">No final report generated yet.</p>
        )}
      </Card>

      <Card>
        <SectionTitle title="Transcript" subtitle="Ordered interview conversation and candidate responses." />

        {messagesError ? <AlertMessage kind="error">{messagesError}</AlertMessage> : null}
        {isLoadingMessages ? <p className="muted">Loading transcript...</p> : null}

        {!isLoadingMessages && messages.length === 0 ? (
          <p className="muted">No messages yet.</p>
        ) : (
          <div className="chat-thread">
            {messages.map((message) => (
              <article
                key={message.id}
                className={`chat-row chat-${message.role === "candidate" ? "candidate" : "assistant"}`}
              >
                <div className="chat-bubble">
                  <div className="chat-meta">
                    <span className="chat-role">{message.role.toUpperCase()}</span>
                    {message.question_number ? <span>Q{message.question_number}</span> : null}
                    {message.created_at ? <span>{formatDate(message.created_at)}</span> : null}
                  </div>
                  <p>{message.content}</p>
                </div>
              </article>
            ))}
          </div>
        )}
      </Card>
    </PageContainer>
  );
}
