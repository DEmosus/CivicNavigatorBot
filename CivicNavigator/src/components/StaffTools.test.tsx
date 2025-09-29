import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import StaffTools from "./StaffTools";
import * as api from "../utils/api";
import * as auth from "../utils/auth";
import { vi } from "vitest";

vi.mock("../utils/api");
vi.mock("../utils/auth");

describe("StaffTools", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (auth.isStaff as vi.Mock).mockReturnValue(true);
  });

  it("renders KB search and incidents", async () => {
    // Mock KB search
    (api.getKbDocs as vi.Mock).mockResolvedValue({
      results: [
        {
          doc_id: "kb1",
          title: "Garbage Collection Schedule",
          snippet: "Garbage is collected...",
          score: 0.95,
          source_url: "https://city.gov/garbage-schedule",
        },
      ],
    });

    // Mock incidents
    (api.getAllIncidents as vi.Mock).mockResolvedValue([
      {
        incident_id: "INC-1",
        title: "Water leak",
        category: "water_supply",
        status: "NEW",
        created_at: "2025-08-13T08:07:14.335303",
        updated_at: "2025-08-13T08:07:14",
        priority: "HIGH",
        description: "Leak in pipe",
      },
    ]);

    render(<StaffTools />);

    // Wait for incident to be displayed
    await waitFor(() => {
      expect(screen.getByText(/Water leak/i)).toBeInTheDocument();
    });

    // KB search
    fireEvent.change(screen.getByLabelText(/Knowledge base search/i), {
      target: { value: "garbage" },
    });
    fireEvent.click(screen.getByRole("button", { name: /search kb/i }));

    await waitFor(() => {
      expect(screen.getByText(/Garbage Collection Schedule/i)).toBeInTheDocument();
    });
  });

  it("updates incident status", async () => {
    (api.getKbDocs as vi.Mock).mockResolvedValue({ results: [] });
    (api.getAllIncidents as vi.Mock).mockResolvedValue([
      {
        incident_id: "INC-1",
        title: "Water leak",
        category: "water_supply",
        status: "NEW",
        created_at: "2025-08-13T08:07:14.335303",
        updated_at: "2025-08-13T08:07:14",
        priority: "HIGH",
      },
    ]);
    (api.updateIncidentStatus as vi.Mock).mockResolvedValue({
      incident_id: "INC-1",
      status: "IN_PROGRESS",
      last_update: "2025-08-13T09:00:00",
    });

    render(<StaffTools />);

    // Wait for incident
    await waitFor(() => {
      expect(screen.getByText(/Water leak/i)).toBeInTheDocument();
    });

    // Change status
    fireEvent.change(screen.getByLabelText(/Update status for INC-1/i), {
      target: { value: "IN_PROGRESS" },
    });

    await waitFor(() => {
      expect(api.updateIncidentStatus).toHaveBeenCalledWith(
        "INC-1",
        "IN_PROGRESS"
      );
    });
  });
});
