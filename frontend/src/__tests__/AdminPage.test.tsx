import { render, screen, fireEvent, waitFor, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { AdminPage } from "../pages/AdminPage";
import { API_URL } from "../api/client";

const MOCK_INTERVIEWS = [
  {
    id: "111e4567-e89b-12d3-a456-426614174001",
    status: "DRAFT",
    title: "First Interview",
    target_questions: 8,
    current_question_number: 0,
    current_difficulty: 5,
    match_analysis_json: null,
    report_json: null,
  },
  {
    id: "222e4567-e89b-12d3-a456-426614174002",
    status: "READY",
    title: "Second Interview",
    target_questions: 5,
    current_question_number: 0,
    current_difficulty: 5,
    match_analysis_json: null,
    report_json: null,
  },
];

const MOCK_DOCUMENTS = {
  interview_id: "111e4567-e89b-12d3-a456-426614174001",
  documents: [
    {
      id: "d1",
      interview_id: "111e4567-e89b-12d3-a456-426614174001",
      document_type: "resume" as const,
      filename: "resume.pdf",
      storage_path: "resume.pdf",
      mime_type: "application/pdf",
      extracted_text: "text",
      extracted_character_count: 100,
      created_at: "2025-01-01T00:00:00Z",
    },
  ],
};

function renderAdminPage() {
  return render(
    <MemoryRouter>
      <AdminPage />
    </MemoryRouter>
  );
}

describe("AdminPage", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders workflow card and create form", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => [],
    } as Response);

    renderAdminPage();

    expect(screen.getByText("Workflow")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Create Interview" })
    ).toBeInTheDocument();
  });

  it("loads and displays interview list", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => MOCK_INTERVIEWS,
    } as Response);

    renderAdminPage();

    await waitFor(() => {
      expect(screen.getByText("Existing Interviews")).toBeInTheDocument();
    });
    expect(screen.getByText("First Interview")).toBeInTheDocument();
    expect(screen.getByText("Second Interview")).toBeInTheDocument();
  });

  it("shows error when list fetch fails", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("Network error"));

    renderAdminPage();

    await waitFor(() => {
      expect(screen.getByText("Could not load interviews.")).toBeInTheDocument();
    });
  });

  it("opens confirm dialog on delete click", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => MOCK_INTERVIEWS,
    } as Response);

    renderAdminPage();

    await waitFor(() => {
      expect(screen.getByText("First Interview")).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByRole("button", { name: "Delete" });
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(screen.getByRole("dialog")).toBeInTheDocument();
    });
    expect(screen.getByText("Delete Interview")).toBeInTheDocument();
  });

  it("cancels deletion when cancel is clicked", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => MOCK_INTERVIEWS,
    } as Response);

    renderAdminPage();

    await waitFor(() => {
      expect(screen.getByText("First Interview")).toBeInTheDocument();
    });

    fireEvent.click(screen.getAllByRole("button", { name: "Delete" })[0]);

    await waitFor(() => {
      expect(screen.getByText("Delete Interview")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Cancel"));

    await waitFor(() => {
      expect(screen.queryByText("Delete Interview")).not.toBeInTheDocument();
    });
  });

  it("deletes interview after confirmation", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch");

    fetchMock.mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      const method = init?.method || "GET";
      const url = typeof input === "string" ? input : input.toString();

      if (method === "GET" && url === `${API_URL}/interviews`) {
        return { ok: true, json: async () => MOCK_INTERVIEWS } as Response;
      }
      if (method === "GET" && url.includes("/documents")) {
        return { ok: true, json: async () => MOCK_DOCUMENTS } as Response;
      }
      if (method === "DELETE" && url.includes("/documents/")) {
        return { ok: true, json: async () => undefined } as Response;
      }
      if (method === "DELETE") {
        return { ok: true, status: 204, json: async () => undefined } as Response;
      }
      return { ok: true, json: async () => [] } as Response;
    });

    renderAdminPage();

    await waitFor(() => {
      expect(screen.getByText("First Interview")).toBeInTheDocument();
    });

    fireEvent.click(screen.getAllByRole("button", { name: "Delete" })[0]);

    await waitFor(() => {
      expect(screen.getByRole("dialog")).toBeInTheDocument();
    });

    const confirmBtn = within(screen.getByRole("dialog")).getByRole("button", { name: "Delete" });
    fireEvent.click(confirmBtn);

    await waitFor(() => {
      expect(screen.queryByText("First Interview")).not.toBeInTheDocument();
    });

    expect(screen.getByText("Second Interview")).toBeInTheDocument();
  });
});
