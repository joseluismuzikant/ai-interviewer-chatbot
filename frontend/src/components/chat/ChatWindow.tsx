import type { MessageResponse } from "../../types/message";
import type { StartQuestion } from "../../types/interview";
import type { AnswerEvaluation } from "../../types/report";
import { MessageBubble } from "./MessageBubble";
import { AnswerInput } from "./AnswerInput";
import { EvaluationPanel } from "./EvaluationPanel";
import { Card } from "../common/Card";

type ChatWindowProps = {
  messages: MessageResponse[];
  question: StartQuestion | null;
  answerText: string;
  onAnswerChange: (text: string) => void;
  onPasteDetected: () => void;
  onSubmitAnswer: () => void;
  isSubmitting: boolean;
  isCompleted: boolean;
  evaluation: AnswerEvaluation | null;
};

export function ChatWindow({
  messages,
  question,
  answerText,
  onAnswerChange,
  onPasteDetected,
  onSubmitAnswer,
  isSubmitting,
  isCompleted,
  evaluation,
}: ChatWindowProps) {
  if (!question && messages.length === 0 && !isCompleted) return null;

  return (
    <>
      {messages.length > 0 ? (
        <Card>
          <h4 className="section-title">Transcript</h4>
          <div className="chat-thread">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
          </div>
        </Card>
      ) : null}

      {question ? (
        <Card>
          <div className="question-content">
            <p className="question-text">{question.content}</p>
          </div>
          <div className="question-meta-row">
            <div className="meta-pill">
              <span>Topic</span>
              <strong>{question.topic}</strong>
            </div>
            <div className="meta-pill">
              <span>Difficulty</span>
              <strong>{question.difficulty}</strong>
            </div>
          </div>
          {!isCompleted ? (
            <AnswerInput
              value={answerText}
              onChange={onAnswerChange}
              onPaste={onPasteDetected}
              onSubmit={onSubmitAnswer}
              disabled={isSubmitting}
            />
          ) : null}
          {evaluation ? <EvaluationPanel evaluation={evaluation} /> : null}
        </Card>
      ) : null}
    </>
  );
}
