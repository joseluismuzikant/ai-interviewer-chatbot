import type { AnswerEvaluation } from "../../types/report";

type EvaluationPanelProps = {
  evaluation: AnswerEvaluation;
};

export function EvaluationPanel({ evaluation }: EvaluationPanelProps) {
  return (
    <div className="report-layout" style={{ marginTop: "1rem" }}>
      <div className="report-metrics">
        <div className="metric-card metric-accent">
          <span className="metric-label">Score</span>
          <strong className="metric-value">{evaluation.score}</strong>
        </div>
      </div>
      <div className="summary-card card">
        <h4>Rationale</h4>
        <p>{evaluation.rationale}</p>
      </div>
      <div className="summary-card card">
        <h4>Evidence</h4>
        <p>{evaluation.evidence}</p>
      </div>
      <div className="summary-card card">
        <h4>Follow-up Hint</h4>
        <p>{evaluation.followup_hint}</p>
      </div>
    </div>
  );
}
