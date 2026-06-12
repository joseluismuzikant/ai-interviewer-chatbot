import { FormEvent, useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import {
  DocumentType,
  InterviewResponse,
  UploadDocumentResponse,
  getInterviews,
  uploadInterviewDocument,
} from "../api/client";

type UploadState = {
  isUploading: boolean;
  message: string | null;
};

export function AdminInterviewDetailsPage() {
  const { id } = useParams();
  const [interviews, setInterviews] = useState<InterviewResponse[]>([]);
  const [selectedInterviewId, setSelectedInterviewId] = useState("");
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
    } catch (error) {
      setState({
        isUploading: false,
        message: error instanceof Error ? error.message : "Upload failed",
      });
    }
  }

  return (
    <section>
      <h2>Interview Details</h2>
      <p>Interview created successfully.</p>
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
                {interview.title?.trim() || `Untitled interview (${interview.id})`}
              </option>
            ))
          )}
        </select>
      </label>

      {isLoadingInterviews ? <p>Loading interviews...</p> : null}
      {interviewsError ? <p className="form-error">{interviewsError}</p> : null}
      {selectedInterviewId ? <p>Selected Interview ID: {selectedInterviewId}</p> : null}

      <div className="upload-grid">
        <form
          className="upload-card"
          onSubmit={(event) => submitUpload(event, "resume")}
        >
          <h3>Upload Resume</h3>
          <input
            type="file"
            accept="application/pdf,.pdf"
            onChange={(event) =>
              setResumeFile(event.target.files?.[0] ?? null)
            }
          />
          <button
            type="submit"
            disabled={resumeState.isUploading || !selectedInterviewId}
          >
            {resumeState.isUploading ? "Uploading..." : "Upload Resume"}
          </button>
          {resumeState.message ? <p>{resumeState.message}</p> : null}
        </form>

        <form
          className="upload-card"
          onSubmit={(event) => submitUpload(event, "role_description")}
        >
          <h3>Upload Role Description</h3>
          <input
            type="file"
            accept="application/pdf,.pdf"
            onChange={(event) => setRoleFile(event.target.files?.[0] ?? null)}
          />
          <button
            type="submit"
            disabled={roleState.isUploading || !selectedInterviewId}
          >
            {roleState.isUploading ? "Uploading..." : "Upload Role Description"}
          </button>
          {roleState.message ? <p>{roleState.message}</p> : null}
        </form>
      </div>
    </section>
  );
}
