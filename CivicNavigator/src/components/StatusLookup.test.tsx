import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import StatusLookup from "./StatusLookup";
import { getIncidentStatus } from "../utils/api";
import { vi } from "vitest";
import type { Mock } from "vitest";

// 🧪 Mock the API
vi.mock("../utils/api", () => ({
  getIncidentStatus: vi.fn(),
}));

describe("StatusLookup", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders input and lookup button", () => {
    render(<StatusLookup />);
    expect(screen.getByPlaceholderText(/incident id/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /check/i })).toBeInTheDocument();
  });

  it("fetches and displays incident status", async () => {
    (getIncidentStatus as Mock).mockResolvedValue({
      status: "IN_PROGRESS",
      last_update: "2025-08-01T10:00:00Z",
      history: [
        { timestamp: "2025-08-01T08:00:00Z", status: "NEW" },
        { timestamp: "2025-08-01T10:00:00Z", status: "IN_PROGRESS" },
      ],
    });

    render(<StatusLookup />);

    fireEvent.change(screen.getByPlaceholderText(/incident id/i), {
      target: { value: "12345" },
    });

    fireEvent.click(screen.getByRole("button", { name: /check/i }));

    await waitFor(() => {
      const statusParagraphs = screen.getAllByText((content) =>
        content.includes("IN_PROGRESS")
      );
      expect(statusParagraphs.length).toBeGreaterThan(0);

      expect(screen.getByText(/last updated/i)).toBeInTheDocument();
    });
  });

  it("shows error if status not found", async () => {
    (getIncidentStatus as Mock).mockRejectedValue(new Error("Not found"));

    render(<StatusLookup />);

    fireEvent.change(screen.getByPlaceholderText(/incident id/i), {
      target: { value: "99999" },
    });

    fireEvent.click(screen.getByRole("button", { name: /check/i }));

    await waitFor(() => {
      expect(
        screen.getByText(/incident not found/i)
      ).toBeInTheDocument();
    });
  });
});
