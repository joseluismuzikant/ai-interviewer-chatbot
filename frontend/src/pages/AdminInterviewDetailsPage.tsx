import { useParams } from "react-router-dom";

export function AdminInterviewDetailsPage() {
  const { id } = useParams();

  return (
    <section>
      <h2>Interview Details</h2>
      <p>Interview ID: {id}</p>
      <p>Placeholder for resume upload, role description upload, and analysis.</p>
    </section>
  );
}
