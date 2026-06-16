type AnswerInputProps = {
  value: string;
  onChange: (text: string) => void;
  onPaste: () => void;
  onSubmit: () => void;
  disabled?: boolean;
};

export function AnswerInput({ value, onChange, onPaste, onSubmit, disabled }: AnswerInputProps) {
  return (
    <div className="answer-form-block">
      <label htmlFor="candidate-answer" className="meta-label">
        Your Answer
      </label>
      <textarea
        id="candidate-answer"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onPaste={onPaste}
        rows={8}
        placeholder="Type your answer here..."
        disabled={disabled}
      />
      {disabled ? (
        <p className="muted">Evaluating answer and preparing next question...</p>
      ) : null}
      <button type="button" onClick={onSubmit} disabled={disabled}>
        {disabled ? "Submitting..." : "Submit Answer"}
      </button>
    </div>
  );
}
