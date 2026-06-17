import type { MessageResponse } from "../../types/message";

type MessageBubbleProps = {
  message: MessageResponse;
};

function formatDate(value: string | null): string {
  if (!value) return "";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "";
  return parsed.toLocaleString();
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const roleClass = message.role === "candidate" ? "candidate" : "assistant";
  return (
    <article className={`chat-row chat-${roleClass}`}>
      <div className="chat-bubble">
        <div className="chat-meta">
          <span className="chat-role">{message.role.toUpperCase()}</span>
          {message.question_number ? <span>Q{message.question_number}</span> : null}
          {message.created_at ? <span>{formatDate(message.created_at)}</span> : null}
          {message.role === "candidate" && message.paste_detected ? (
            <span className="paste-badge">PASTED</span>
          ) : null}
        </div>
        <p>{message.content}</p>
      </div>
    </article>
  );
}
