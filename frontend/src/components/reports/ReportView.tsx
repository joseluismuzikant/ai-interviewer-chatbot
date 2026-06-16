import type { FinalReportResponse } from "../../types/interview";
import { Card } from "../common/Card";
import { ScoreSummary } from "./ScoreSummary";
import { EmptyState } from "../common/EmptyState";

type ReportViewProps = {
  report: FinalReportResponse | null;
  status?: string | null;
};

export function ReportView({ report, status }: ReportViewProps) {
  if (!report) {
    if (status === "COMPLETED") {
      return <EmptyState message="No final report generated yet." />;
    }
    return null;
  }

  return (
    <div className="report-layout">
      <ScoreSummary
        overallScore={report.overall_score}
        recommendation={report.recommendation}
      />
      <Card className="summary-card">
        <h4>Recommendation Rationale</h4>
        <p>{report.recommendation_rationale}</p>
      </Card>
      <Card className="summary-card">
        <h4>Summary</h4>
        <p>{report.summary}</p>
      </Card>
      <div className="report-columns">
        <Card>
          <h4>Strengths</h4>
          {report.strengths.length === 0 ? (
            <p className="muted">No strengths listed.</p>
          ) : (
            <ul>
              {report.strengths.map((item, idx) => (
                <li key={`s-${idx}`}>{item}</li>
              ))}
            </ul>
          )}
        </Card>
        <Card>
          <h4>Weaknesses</h4>
          {report.weaknesses.length === 0 ? (
            <p className="muted">No weaknesses listed.</p>
          ) : (
            <ul>
              {report.weaknesses.map((item, idx) => (
                <li key={`w-${idx}`}>{item}</li>
              ))}
            </ul>
          )}
        </Card>
      </div>
      {report.integrity_notes.length > 0 ? (
        <Card>
          <h4>Integrity Notes</h4>
          <ul>
            {report.integrity_notes.map((item, idx) => (
              <li key={`i-${idx}`}>{item}</li>
            ))}
          </ul>
        </Card>
      ) : null}
    </div>
  );
}
