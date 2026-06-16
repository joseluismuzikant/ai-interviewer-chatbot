type ScoreSummaryProps = {
  overallScore: number;
  recommendation: "YES" | "MIXED" | "NO";
};

export function ScoreSummary({ overallScore, recommendation }: ScoreSummaryProps) {
  return (
    <div className="report-metrics">
      <div className="metric-card metric-accent">
        <span className="metric-label">Overall Score</span>
        <strong className="metric-value">{overallScore}</strong>
      </div>
      <div className="metric-card metric-neutral">
        <span className="metric-label">Recommendation</span>
        <strong
          className={`recommendation-badge recommendation-${recommendation.toLowerCase()}`}
        >
          {recommendation}
        </strong>
      </div>
    </div>
  );
}
