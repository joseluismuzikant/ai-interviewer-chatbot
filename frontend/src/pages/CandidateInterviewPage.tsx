import { useParams } from "react-router-dom";

export function CandidateInterviewPage() {
  const { id } = useParams();

  return (
    <section>
      <h2>Candidate Interview</h2>
      <p>Interview ID: {id}</p>
      <p>Placeholder for interview chat experience.</p>
    </section>
  );
}
