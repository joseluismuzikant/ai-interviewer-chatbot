import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { EvaluationPanel } from "../components/chat/EvaluationPanel";

describe("EvaluationPanel", () => {
  const evaluation = {
    score: 8,
    rationale: "Good understanding demonstrated",
    evidence: "Candidate explained DI clearly",
    followup_hint: "Ask about containers",
  };

  it("renders score", () => {
    render(<EvaluationPanel evaluation={evaluation} />);
    expect(screen.getByText("8")).toBeInTheDocument();
  });

  it("renders rationale", () => {
    render(<EvaluationPanel evaluation={evaluation} />);
    expect(screen.getByText("Good understanding demonstrated")).toBeInTheDocument();
  });

  it("renders evidence", () => {
    render(<EvaluationPanel evaluation={evaluation} />);
    expect(screen.getByText("Candidate explained DI clearly")).toBeInTheDocument();
  });

  it("renders followup_hint", () => {
    render(<EvaluationPanel evaluation={evaluation} />);
    expect(screen.getByText("Ask about containers")).toBeInTheDocument();
  });
});
