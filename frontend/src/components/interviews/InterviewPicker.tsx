import type { InterviewResponse } from "../../types/interview";

type InterviewPickerProps = {
  interviews: InterviewResponse[];
  selectedId: string;
  onChange: (id: string) => void;
  disabled?: boolean;
};

function shortId(id: string): string {
  if (id.length <= 16) return id;
  return `${id.slice(0, 8)}...${id.slice(-6)}`;
}

export function InterviewPicker({ interviews, selectedId, onChange, disabled }: InterviewPickerProps) {
  return (
    <label className="interview-picker">
      Interview
      <select
        value={selectedId}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled || interviews.length === 0}
      >
        {interviews.length === 0 ? (
          <option value="">No interviews available</option>
        ) : (
          interviews.map((interview) => (
            <option key={interview.id} value={interview.id}>
              {interview.title?.trim() || `Untitled interview (${shortId(interview.id)})`}
            </option>
          ))
        )}
      </select>
    </label>
  );
}
