import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "../App";

describe("App", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => [],
    } as Response);
  });

  it("renders without crashing and shows the admin page by default", async () => {
    render(
      <MemoryRouter initialEntries={["/admin"]}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByRole("heading", { name: "AI Interviewer Chatbot" })).toBeInTheDocument();
    expect(screen.getByText("MVP Demo")).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Admin" })).toBeInTheDocument();
  });

  it("redirects root to /admin", async () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>
    );
    expect(await screen.findByRole("heading", { name: "Admin" })).toBeInTheDocument();
  });
});
