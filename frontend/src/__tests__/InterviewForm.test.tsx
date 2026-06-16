import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { InterviewForm } from "../components/interviews/InterviewForm";

describe("InterviewForm", () => {
  it("renders required fields", () => {
    render(<InterviewForm onSubmit={vi.fn()} />);
    expect(screen.getByPlaceholderText("e.g. Backend Engineer Interview")).toBeInTheDocument();
    expect(screen.getByText("Target questions")).toBeInTheDocument();
    expect(screen.getByText("Starting difficulty")).toBeInTheDocument();
    expect(screen.getByText("Create Interview")).toBeInTheDocument();
  });

  it("allows typing values", async () => {
    render(<InterviewForm onSubmit={vi.fn()} />);
    const titleInput = screen.getByPlaceholderText("e.g. Backend Engineer Interview");
    await userEvent.type(titleInput, "Frontend Interview");
    expect(titleInput).toHaveValue("Frontend Interview");
  });

  it("calls submit handler with expected values", async () => {
    const onSubmit = vi.fn();
    render(<InterviewForm onSubmit={onSubmit} />);

    const titleInput = screen.getByPlaceholderText("e.g. Backend Engineer Interview");
    await userEvent.type(titleInput, "Test Interview");

    const tqInput = screen.getByLabelText("Target questions");
    fireEvent.change(tqInput, { target: { value: "5" } });

    const sdInput = screen.getByLabelText("Starting difficulty");
    fireEvent.change(sdInput, { target: { value: "6" } });

    fireEvent.click(screen.getByText("Create Interview"));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        title: "Test Interview",
        target_questions: 5,
        starting_difficulty: 6,
      });
    });
  });
});
