import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../utils/api";
import * as auth from "../utils/auth";
import StaffTools from "./StaffTools";

vi.mock("../utils/api");
vi.mock("../utils/auth");

describe("StaffTools", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (auth.isStaff as vi.Mock).mockReturnValue(true);
  });

  it("renders KB search and incidents", async () => {
    (api.searchStaffKb as vi.Mock).mockResolvedValue({
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

    (api.getAllIncidents as vi.Mock).mockResolvedValue([
      {
        incident_id: "INC-1",
        title: "Water leak",
        category: "water_supply",
        status: "new",
        created_at: "2025-08-13T08:07:14.335303",
        last_update: "2025-08-13T08:07:14",
        priority: "HIGH",
        description: "Leak in pipe",
      },
    ]);

    render(<StaffTools />);

    await waitFor(() => {
      expect(screen.getByText(/Water leak/i)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/Knowledge base search/i), {
      target: { value: "garbage" },
    });
    fireEvent.click(screen.getByRole("button", { name: /search kb/i }));

    await waitFor(() => {
      expect(
        screen.getByText(/Garbage Collection Schedule/i)
      ).toBeInTheDocument();
    });
  });

  it("updates incident status", async () => {
    (api.searchStaffKb as vi.Mock).mockResolvedValue({ results: [] });
    (api.getAllIncidents as vi.Mock).mockResolvedValue([
      {
        incident_id: "INC-1",
        title: "Water leak",
        category: "water_supply",
        status: "new",
        created_at: "2025-08-13T08:07:14.335303",
        last_update: "2025-08-13T08:07:14",
        priority: "HIGH",
      },
    ]);
    (api.updateIncidentStatus as vi.Mock).mockResolvedValue({
      incident_id: "INC-1",
      status: "in_progress",
      last_update: "2025-08-13T09:00:00",
    });

    render(<StaffTools />);

    await waitFor(() => {
      expect(screen.getByText(/Water leak/i)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/Update status for INC-1/i), {
      target: { value: "in_progress" },
    });

    await waitFor(() => {
      expect(api.updateIncidentStatus).toHaveBeenCalledWith(
        "INC-1",
        "in_progress"
      );
    });
  });
});
