import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ReportView } from "../components/reports/ReportView";

const FULL_REPORT = {
  summary: "Good technical skills",
  overall_score: 7.5,
  strengths: ["Communication", "Problem solving"],
  weaknesses: ["Cloud experience"],
  integrity_notes: [],
  recommendation: "YES" as const,
  recommendation_rationale: "Strong fit for the role",
};

describe("ReportView", () => {
  it("renders nothing when report is null and status is not COMPLETED", () => {
    const { container } = render(<ReportView report={null} status="DRAFT" />);
    expect(container.innerHTML).toBe("");
  });

  it("renders empty state when report is null but status is COMPLETED", () => {
    render(<ReportView report={null} status="COMPLETED" />);
    expect(screen.getByText("No final report generated yet.")).toBeInTheDocument();
  });

  it("renders summary and recommendation", () => {
    render(<ReportView report={FULL_REPORT} status="COMPLETED" />);
    expect(screen.getByText("Good technical skills")).toBeInTheDocument();
    expect(screen.getByText("YES")).toBeInTheDocument();
    expect(screen.getByText("7.5")).toBeInTheDocument();
  });

  it("renders recommendation rationale", () => {
    render(<ReportView report={FULL_REPORT} status="COMPLETED" />);
    expect(screen.getByText("Strong fit for the role")).toBeInTheDocument();
  });

  it("renders strengths and weaknesses", () => {
    render(<ReportView report={FULL_REPORT} status="COMPLETED" />);
    expect(screen.getByText("Communication")).toBeInTheDocument();
    expect(screen.getByText("Problem solving")).toBeInTheDocument();
    expect(screen.getByText("Cloud experience")).toBeInTheDocument();
  });

  it("renders integrity notes when present", () => {
    const reportWithIntegrity = {
      ...FULL_REPORT,
      integrity_notes: ["Paste detected in answer 2"],
    };
    render(<ReportView report={reportWithIntegrity} status="COMPLETED" />);
    expect(screen.getByText("Paste detected in answer 2")).toBeInTheDocument();
  });
});
