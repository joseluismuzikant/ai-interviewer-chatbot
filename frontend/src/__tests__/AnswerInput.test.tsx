import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { AnswerInput } from "../components/chat/AnswerInput";

describe("AnswerInput", () => {
  it("renders textarea and submit button", () => {
    render(
      <AnswerInput
        value=""
        onChange={vi.fn()}
        onPaste={vi.fn()}
        onSubmit={vi.fn()}
      />
    );
    expect(screen.getByPlaceholderText("Type your answer here...")).toBeInTheDocument();
    expect(screen.getByText("Submit Answer")).toBeInTheDocument();
  });

  it("calls onChange when typing", () => {
    const onChange = vi.fn();
    render(
      <AnswerInput
        value=""
        onChange={onChange}
        onPaste={vi.fn()}
        onSubmit={vi.fn()}
      />
    );
    const textarea = screen.getByPlaceholderText("Type your answer here...");
    fireEvent.change(textarea, { target: { value: "hello" } });
    expect(onChange).toHaveBeenCalledWith("hello");
  });

  it("calls onSubmit when button clicked", () => {
    const onSubmit = vi.fn();
    render(
      <AnswerInput
        value="my answer"
        onChange={vi.fn()}
        onPaste={vi.fn()}
        onSubmit={onSubmit}
      />
    );
    fireEvent.click(screen.getByText("Submit Answer"));
    expect(onSubmit).toHaveBeenCalled();
  });

  it("shows submitting state", () => {
    render(
      <AnswerInput
        value="answer"
        onChange={vi.fn()}
        onPaste={vi.fn()}
        onSubmit={vi.fn()}
        disabled={true}
      />
    );
    expect(screen.getByText("Submitting...")).toBeDisabled();
    expect(screen.getByText(/Evaluating answer/)).toBeInTheDocument();
  });

  it("detects paste events", () => {
    const onPaste = vi.fn();
    render(
      <AnswerInput
        value=""
        onChange={vi.fn()}
        onPaste={onPaste}
        onSubmit={vi.fn()}
      />
    );
    const textarea = screen.getByPlaceholderText("Type your answer here...");
    fireEvent.paste(textarea, { clipboardData: new DataTransfer() });
    expect(onPaste).toHaveBeenCalled();
  });
});
