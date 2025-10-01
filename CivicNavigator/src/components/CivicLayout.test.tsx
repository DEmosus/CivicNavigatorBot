import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import CivicLayout from "./CivicLayout";

// Mock auth utils
vi.mock("../utils/auth", () => ({
  getToken: vi.fn(),
  logout: vi.fn(),
}));

import { getToken, logout } from "../utils/auth";

// Mock child components (not RoleToggle, we use the real one)
vi.mock("./ChatInterface", () => ({
  default: () => <div data-testid="chat-screen">Chat Screen</div>,
}));

vi.mock("./IncidentForm", () => ({
  default: () => <div data-testid="incident-form">Incident Form</div>,
}));

vi.mock("./StatusLookup", () => ({
  default: () => <div data-testid="status-lookup">Status Lookup</div>,
}));

vi.mock("./StaffTools", () => ({
  default: () => <div data-testid="staff-tools">Staff Tools</div>,
}));

vi.mock("./LoginForm", () => ({
  default: ({ onLogin }: { onLogin: () => void }) => (
    <button data-testid="mock-login" onClick={onLogin}>
      Mock Login
    </button>
  ),
}));

vi.mock("./RegisterForm", () => ({
  default: ({ onRegister }: { onRegister: () => void }) => (
    <button data-testid="mock-register" onClick={onRegister}>
      Mock Register
    </button>
  ),
}));

describe("CivicLayout", () => {
  const setup = (token: string | null = null) => {
    (getToken as vi.Mock).mockReturnValue(token);
    const user = userEvent.setup();
    render(<CivicLayout />);
    return { user };
  };

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear(); // reset role before each test
  });

  it("shows resident tabs and ChatInterface initially when not logged in", () => {
    setup();
    expect(
      screen.getByRole("button", { name: /ask services/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /report incident/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /check status/i })
    ).toBeInTheDocument();
    expect(screen.getByTestId("chat-screen")).toBeInTheDocument();
  });

  it("switches to staff role (logged out) and shows Staff Tools tab plus login/register", async () => {
    const { user } = setup();
    await user.selectOptions(screen.getByLabelText(/role/i), "staff");
    expect(
      screen.getByRole("button", { name: /staff tools/i })
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /login/i })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /register/i })
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /logout/i })
    ).not.toBeInTheDocument();
  });

  it("shows login form when viewing staff tools while logged out", async () => {
    const { user } = setup();
    await user.selectOptions(screen.getByLabelText(/role/i), "staff");
    await user.click(screen.getByRole("button", { name: /staff tools/i }));
    // Instead of a text message, we expect the mocked login form
    expect(screen.getByTestId("mock-login")).toBeInTheDocument();
  });

  it("renders StaffTools when logged in as staff", async () => {
    const { user } = setup("token123");
    await user.selectOptions(screen.getByLabelText(/role/i), "staff");
    await user.click(screen.getByRole("button", { name: /staff tools/i }));
    expect(screen.getByTestId("staff-tools")).toBeInTheDocument();
  });

  it("renders IncidentForm when 'Report Incident' is clicked as resident", async () => {
    const { user } = setup();
    await user.selectOptions(screen.getByLabelText(/role/i), "resident");
    await user.click(screen.getByRole("button", { name: /report incident/i }));
    expect(screen.getByTestId("incident-form")).toBeInTheDocument();
  });

  it("renders StatusLookup when 'Check Status' is clicked as resident", async () => {
    const { user } = setup();
    await user.selectOptions(screen.getByLabelText(/role/i), "resident");
    await user.click(screen.getByRole("button", { name: /check status/i }));
    expect(screen.getByTestId("status-lookup")).toBeInTheDocument();
  });

  it("calls logout and resets to Chat tab when logout is clicked", async () => {
    const { user } = setup("token123");
    await user.selectOptions(screen.getByLabelText(/role/i), "staff");
    await screen.findByRole("button", { name: /logout/i });
    await user.click(screen.getByRole("button", { name: /logout/i }));
    expect(logout).toHaveBeenCalled();
    expect(screen.getByTestId("chat-screen")).toBeInTheDocument();
  });

  it("login flow switches to Staff Tools tab", async () => {
    const { user } = setup();
    await user.selectOptions(screen.getByLabelText(/role/i), "staff");
    await user.click(screen.getByRole("button", { name: /login/i }));
    await user.click(screen.getByTestId("mock-login"));
    expect(screen.getByTestId("staff-tools")).toBeInTheDocument();
  });

  it("resets tab to 'chat' when switching back to resident role", async () => {
    const { user } = setup();
    await user.selectOptions(screen.getByLabelText(/role/i), "staff");
    await user.selectOptions(screen.getByLabelText(/role/i), "resident");
    expect(
      await screen.findByRole("button", { name: /report incident/i })
    ).toBeInTheDocument();
    expect(screen.getByTestId("chat-screen")).toBeInTheDocument();
  });

  it("shows logout button when logged in as staff", async () => {
    const { user } = setup("token123");
    await user.selectOptions(screen.getByLabelText(/role/i), "staff");
    expect(
      await screen.findByRole("button", { name: /logout/i })
    ).toBeInTheDocument();
  });
});
