import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createIncident } from "../utils/api";
import IncidentForm from "./IncidentForm";

// Mock the API
vi.mock("../utils/api", () => ({
  createIncident: vi.fn(),
}));

const mockedCreateIncident = vi.mocked(createIncident);

describe("IncidentForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // Helper to ensure required fields pass validation
  const fillMinimumValidFields = async () => {
    await userEvent.type(
      screen.getByLabelText(/incident title/i),
      "Valid Title"
    );
    await userEvent.selectOptions(
      screen.getByLabelText(/incident category/i),
      "road_maintenance"
    );
    await userEvent.type(
      screen.getByLabelText(/incident description/i),
      "Valid description"
    );
  };

  it("renders form fields correctly", () => {
    render(<IncidentForm />);
    expect(
      screen.getByRole("heading", { name: /report an incident/i })
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/incident title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/incident category/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/incident location/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contact email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/incident description/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /submit incident/i })
    ).toBeInTheDocument();
  });

  it("submits the form and shows success message", async () => {
    mockedCreateIncident.mockResolvedValue({
      incident_id: "INC123",
      status: "submitted",
      created_at: "2024-06-01T12:00:00Z",
    });

    render(<IncidentForm />);

    await userEvent.type(
      screen.getByLabelText(/incident title/i),
      "Water pipe burst"
    );
    await userEvent.selectOptions(
      screen.getByLabelText(/incident category/i),
      "water_supply"
    );
    await userEvent.type(
      screen.getByLabelText(/incident location/i),
      "South B"
    );
    await userEvent.type(
      screen.getByLabelText(/contact email/i),
      "user@example.com"
    );
    await userEvent.type(
      screen.getByLabelText(/incident description/i),
      "Pipe burst near the petrol station"
    );

    expect(
      (screen.getByLabelText(/incident category/i) as HTMLSelectElement).value
    ).toBe("water_supply");

    await userEvent.click(
      screen.getByRole("button", { name: /submit incident/i })
    );

    await waitFor(() => {
      expect(mockedCreateIncident).toHaveBeenCalledTimes(1);
    });

    const status = await screen.findByRole("status");
    expect(status).toHaveTextContent(/incident submitted/i);
    expect(status).toHaveTextContent(/inc123/i);
  });

  it("shows field validation errors from a 422 response", async () => {
    mockedCreateIncident.mockRejectedValue({
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
    mockedCreateIncident.mockRejectedValue({
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
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    });
  });

  it("shows fallback error message on generic failure", async () => {
    mockedCreateIncident.mockRejectedValue(new Error("Failed"));

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
