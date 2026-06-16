import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { DocumentUpload } from "../components/documents/DocumentUpload";

describe("DocumentUpload", () => {
  const defaultProps = {
    documentType: "resume" as const,
    label: "Resume",
    existingDocument: undefined,
    onUpload: vi.fn(),
    disabled: false,
  };

  it("renders upload controls", () => {
    render(<DocumentUpload {...defaultProps} />);
    expect(screen.getByText("Resume")).toBeInTheDocument();
    expect(screen.getByText("Upload Resume")).toBeInTheDocument();
    expect(screen.getByText(/no resume uploaded yet/i)).toBeInTheDocument();
  });

  it("shows existing document info when provided", () => {
    render(
      <DocumentUpload
        {...defaultProps}
        existingDocument={{
          id: "d1",
          interview_id: "i1",
          document_type: "resume",
          filename: "my-resume.pdf",
          storage_path: "path",
          mime_type: "application/pdf",
          extracted_text: null,
          extracted_character_count: 250,
          created_at: null,
        }}
      />
    );
    expect(screen.getByText("my-resume.pdf")).toBeInTheDocument();
    expect(screen.getByText(/250 characters extracted/)).toBeInTheDocument();
  });

  it("accepts a fake PDF file and calls upload handler", async () => {
    const onUpload = vi.fn().mockResolvedValue(undefined);
    render(<DocumentUpload {...defaultProps} onUpload={onUpload} />);

    const file = new File(["%PDF-1.4 fake"], "resume.pdf", { type: "application/pdf" });
    const fileInputs = document.querySelectorAll('input[type="file"]');
    expect(fileInputs.length).toBe(1);
    fireEvent.change(fileInputs[0], { target: { files: [file] } });

    fireEvent.click(screen.getByText("Upload Resume"));

    await waitFor(() => {
      expect(onUpload).toHaveBeenCalledWith(file);
    });
  });
});
