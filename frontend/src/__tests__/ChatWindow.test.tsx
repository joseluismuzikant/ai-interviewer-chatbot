import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ChatWindow } from "../components/chat/ChatWindow";

describe("ChatWindow", () => {
  const baseProps = {
    messages: [],
    question: null,
    answerText: "",
    onAnswerChange: vi.fn(),
    onPasteDetected: vi.fn(),
    onSubmitAnswer: vi.fn(),
    isSubmitting: false,
    isCompleted: false,
    evaluation: null,
  };

  it("renders nothing when there is no question and no messages", () => {
    const { container } = render(<ChatWindow {...baseProps} />);
    expect(container.innerHTML).toBe("");
  });

  it("renders existing messages", () => {
    render(
      <ChatWindow
        {...baseProps}
        messages={[
          {
            id: "m1",
            interview_id: "i1",
            role: "assistant",
            content: "What is your experience?",
            question_number: 1,
            difficulty_level: 5,
            answer_quality_score: null,
            response_time_ms: null,
            paste_detected: null,
            created_at: null,
          },
        ]}
      />
    );
    expect(screen.getByText("What is your experience?")).toBeInTheDocument();
    expect(screen.getByText("Q1")).toBeInTheDocument();
  });

  it("renders current question", () => {
    render(
      <ChatWindow
        {...baseProps}
        question={{
          id: "q1",
          content: "Explain closures in JS",
          topic: "JavaScript",
          difficulty: 5,
          question_number: 1,
          expected_signals: ["Scope", "Lexical environment"],
        }}
      />
    );
    expect(screen.getByText("Explain closures in JS")).toBeInTheDocument();
    expect(screen.getByText("JavaScript")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
  });

  it("allows candidate to type an answer", () => {
    const onAnswerChange = vi.fn();
    render(
      <ChatWindow
        {...baseProps}
        question={{
          id: "q1",
          content: "Explain closures?",
          topic: "JS",
          difficulty: 5,
          question_number: 1,
          expected_signals: [],
        }}
        onAnswerChange={onAnswerChange}
      />
    );
    const textarea = screen.getByPlaceholderText("Type your answer here...");
    fireEvent.change(textarea, { target: { value: "A closure is..." } });
    expect(onAnswerChange).toHaveBeenCalledWith("A closure is...");
  });

  it("submit button sends answer", () => {
    const onSubmitAnswer = vi.fn();
    render(
      <ChatWindow
        {...baseProps}
        question={{
          id: "q1",
          content: "Explain closures?",
          topic: "JS",
          difficulty: 5,
          question_number: 1,
          expected_signals: [],
        }}
        onSubmitAnswer={onSubmitAnswer}
      />
    );
    fireEvent.click(screen.getByText("Submit Answer"));
    expect(onSubmitAnswer).toHaveBeenCalled();
  });

  it("disables input while submitting", () => {
    render(
      <ChatWindow
        {...baseProps}
        question={{
          id: "q1",
          content: "Explain closures?",
          topic: "JS",
          difficulty: 5,
          question_number: 1,
          expected_signals: [],
        }}
        isSubmitting={true}
      />
    );
    expect(screen.getByPlaceholderText("Type your answer here...")).toBeDisabled();
    expect(screen.getByText("Submitting...")).toBeDisabled();
  });
});
