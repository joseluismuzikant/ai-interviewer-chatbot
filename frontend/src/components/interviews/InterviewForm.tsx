import { FormEvent, useState } from "react";
import type { CreateInterviewRequest } from "../../types/interview";

type InterviewFormProps = {
  onSubmit: (payload: CreateInterviewRequest) => Promise<void>;
};

export function InterviewForm({ onSubmit }: InterviewFormProps) {
  const [title, setTitle] = useState("");
  const [targetQuestions, setTargetQuestions] = useState(8);
  const [startingDifficulty, setStartingDifficulty] = useState(5);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit({
        title,
        target_questions: targetQuestions,
        starting_difficulty: startingDifficulty,
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="admin-form" onSubmit={handleSubmit}>
      <label>
        Title
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
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
          onChange={(e) => setTargetQuestions(Number(e.target.value))}
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
          onChange={(e) => setStartingDifficulty(Number(e.target.value))}
        />
      </label>
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Creating interview..." : "Create Interview"}
      </button>
    </form>
  );
}
