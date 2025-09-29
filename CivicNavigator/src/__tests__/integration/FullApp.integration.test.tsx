// src/__tests__/integration/FullApp.integration.test.tsx
import { describe, it, beforeEach, expect, vi } from "vitest";

// Hoist API mock so it's in place before the component is imported
vi.mock("../../utils/api", () => {
  return {
    // Chat
    sendChatMessage: vi.fn().mockResolvedValue({
      reply: "Garbage is collected every Monday and Thursday in Zone A.",
      citations: [],
      confidence: 0.99,
    }),

    // Incidents
    createIncident: vi.fn().mockResolvedValue({
      incident_id: "INC-2025-999",
      status: "NEW",
      created_at: new Date().toISOString(),
    }),
    getIncidentStatus: vi.fn().mockResolvedValue({
      status: "NEW",
      last_update: new Date().toISOString(),
      history: [],
    }),
    getAllIncidents: vi.fn().mockResolvedValue([]),
    updateIncidentStatus: vi.fn().mockResolvedValue({
      incident_id: "INC-2025-999",
      status: "IN_PROGRESS",
      last_update: new Date().toISOString(),
    }),

    // KB
    getKbDocs: vi.fn().mockResolvedValue({
      results: [
        {
          doc_id: "kb1",
          title: "Garbage Collection Schedule",
          snippet:
            "Garbage is collected every Monday and Thursday in Zone A...",
          score: 0.95,
          source_url: "https://city.gov/garbage-schedule",
        },
      ],
    }),
  };
});

import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import CivicLayout from "../../components/CivicLayout";
import * as api from "../../utils/api";

describe("Full App Integration – Resident chat → report → status (mocked backend)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it(
    "completes chat, reports an incident, and looks up status",
    async () => {
      const user = userEvent.setup();
      render(<CivicLayout />);

      // 1) Chat step
      const chatInput = await screen.findByLabelText(/chat input/i);
      await user.type(chatInput, "When is garbage collected?");
      await user.click(screen.getByRole("button", { name: /send/i }));

      expect(
        await screen.findByText(/garbage is collected/i)
      ).toBeInTheDocument();

      // 2) Report Incident
      await user.click(screen.getByRole("button", { name: /report incident/i }));

      await user.type(
        screen.getByLabelText(/title/i),
        "Integration Test – Water leak"
      );
      await user.selectOptions(
        screen.getByLabelText(/category/i),
        "water_supply"
      );
      await user.type(
        screen.getByLabelText(/location/i),
        "Integration Test Location"
      );
      await user.type(
        screen.getByLabelText(/contact_email/i),
        "tester@example.com"
      );
      await user.type(
        screen.getByLabelText(/description/i),
        "This is a test incident created by integration test."
      );

      await user.click(screen.getByRole("button", { name: /submit incident/i }));

      await waitFor(() => {
        expect(api.createIncident).toHaveBeenCalled();
      });

      expect(
        screen.getByText(/INC-2025-999/, { exact: false })
      ).toBeInTheDocument();

      // 3) Status Lookup
      await user.click(screen.getByRole("button", { name: /check status/i }));

      const statusForm = screen.getByRole("form", {
        name: /check incident status/i,
      });

      const idInput = within(statusForm).getByLabelText(/incident id/i);
      await user.clear(idInput);
      await user.type(idInput, "INC-2025-999");
      await user.click(within(statusForm).getByRole("button", { name: /check/i }));

      await waitFor(() => {
        expect(api.getIncidentStatus).toHaveBeenCalledWith("INC-2025-999");
      });

      // Grab <strong>Status:</strong>, then assert on its parent <p>
      const statusLabel = screen.getByText(/status:/i);
      expect(statusLabel.parentElement).not.toBeNull();
      const statusContainer = statusLabel.parentElement as HTMLElement;
      expect(statusContainer).toHaveTextContent(/status:\s*new/i);
    },
    20_000
  );
});
