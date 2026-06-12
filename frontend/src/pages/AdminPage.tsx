import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { createInterview } from "../api/client";

export function AdminPage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [targetQuestions, setTargetQuestions] = useState(8);
  const [startingDifficulty, setStartingDifficulty] = useState(5);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    setIsSubmitting(true);

    try {
      const interview = await createInterview({
        title,
        target_questions: targetQuestions,
        starting_difficulty: startingDifficulty,
      });
      navigate(`/admin/interviews/${interview.id}`);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Could not create interview"
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section>
      <h2>Admin</h2>
      <p>Create and manage interview sessions.</p>

      <form className="admin-form" onSubmit={handleSubmit}>
        <label>
          Title
          <input
            type="text"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="e.g. Backend Engineer Interview"
          />
        </label>

        <label>
          Target questions
          <input
            type="number"
            min={1}
            max={30}
            value={targetQuestions}
            onChange={(event) => setTargetQuestions(Number(event.target.value))}
          />
        </label>

        <label>
          Starting difficulty
          <input
            type="number"
            min={3}
            max={10}
            step={0.5}
            value={startingDifficulty}
            onChange={(event) => setStartingDifficulty(Number(event.target.value))}
          />
        </label>

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Creating..." : "Create Interview"}
        </button>
      </form>

      {errorMessage ? <p className="form-error">{errorMessage}</p> : null}
    </section>
  );
}
