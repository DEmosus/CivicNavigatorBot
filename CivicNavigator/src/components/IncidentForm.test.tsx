import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi, describe, it, expect, beforeEach } from "vitest";
import IncidentForm from "./IncidentForm";
import type { Mock } from "vitest";
import { createIncident } from "../utils/api";

// Mock the API
vi.mock("../utils/api", () => ({
  createIncident: vi.fn(),
}));

describe("IncidentForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // Helper to ensure required fields pass HTML5 validation
  const fillMinimumValidFields = async () => {
    await userEvent.type(screen.getByPlaceholderText(/title/i), "Valid Title");
    await userEvent.selectOptions(
      screen.getByLabelText(/category/i),
      "road_maintenance"
    );
    await userEvent.type(
      screen.getByPlaceholderText(/description/i),
      "Valid description"
    );
  };

  it("renders form fields correctly", () => {
    render(<IncidentForm />);
    expect(
      screen.getByRole("heading", { name: /report incident/i })
    ).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/category/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/location/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/contact/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/description/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /submit incident/i })
    ).toBeInTheDocument();
  });

  it("submits the form and shows success message", async () => {
  (createIncident as Mock<typeof createIncident>).mockResolvedValue({
    incident_id: "INC123",
    status: "submitted",
    created_at: "2024-06-01T12:00:00Z",
  });

  render(<IncidentForm />);

  await userEvent.type(
    screen.getByPlaceholderText(/title/i),
    "Water pipe burst"
  );

  // IMPORTANT: must match an <option value> exactly
  await userEvent.selectOptions(
    screen.getByLabelText(/category/i),
    "water_supply"
  );

  await userEvent.type(
    screen.getByPlaceholderText(/location/i),
    "South B"
  );

  // Leave empty OR use a valid email to pass HTML5 validation
  await userEvent.type(
    screen.getByPlaceholderText(/contact/i),
    "user@example.com"
  );

  await userEvent.type(
    screen.getByPlaceholderText(/description/i),
    "Pipe burst near the petrol station"
  );

  // sanity check: category value really changed
  expect(
    (screen.getByLabelText(/category/i) as HTMLSelectElement).value
  ).toBe("water_supply");

  await userEvent.click(
    screen.getByRole("button", { name: /submit incident/i })
  );

  // verify API call was made
  await waitFor(() => {
    expect(createIncident).toHaveBeenCalledTimes(1);
  });

  // now wait for success message
  const status = await screen.findByRole("status");
  expect(status).toHaveTextContent(/incident submitted/i);
  expect(status).toHaveTextContent(/inc123/i);
}, 10000); // extend timeout


  it("shows field validation errors from a 422 response", async () => {
    (createIncident as Mock<typeof createIncident>).mockRejectedValue({
      response: {
        status: 422,
        data: [
          { loc: ["body", "title"], msg: "Title is required" },
          { loc: ["body", "category"], msg: "Invalid category" },
        ],
      },
    });

    render(<IncidentForm />);
    await fillMinimumValidFields();

    await userEvent.click(
      screen.getByRole("button", { name: /submit incident/i })
    );

    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
      expect(screen.getByText(/invalid category/i)).toBeInTheDocument();
    });
  });

  it("shows general error from a 422 single detail object", async () => {
    (createIncident as Mock<typeof createIncident>).mockRejectedValue({
      response: {
        status: 422,
        data: { detail: "Something went wrong" },
      },
    });

    render(<IncidentForm />);
    await fillMinimumValidFields();

    await userEvent.click(
      screen.getByRole("button", { name: /submit incident/i })
    );

    await waitFor(() => {
      expect(
        screen.getByText(/something went wrong/i)
      ).toBeInTheDocument();
    });
  });

  it("shows fallback error message on generic failure", async () => {
    (createIncident as Mock<typeof createIncident>).mockRejectedValue(
      new Error("Failed")
    );

    render(<IncidentForm />);
    await fillMinimumValidFields();

    await userEvent.click(
      screen.getByRole("button", { name: /submit incident/i })
    );

    await waitFor(() => {
      expect(
        screen.getByText(/failed to submit incident/i)
      ).toBeInTheDocument();
    });
  });
});