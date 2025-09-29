import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import ChatInterface from "./ChatInterface";

// Mock the API call
vi.mock("../utils/api", () => ({
  sendChatMessage: vi.fn(),
}));

import { sendChatMessage } from "../utils/api";
const mockSendChatMessage = sendChatMessage as unknown as jest.Mock;

describe("ChatInterface", () => {
  beforeEach(() => {
    mockSendChatMessage.mockReset();
  });

  it("renders input and send button", () => {
    render(<ChatInterface />);
    expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /send/i })).toBeInTheDocument();
  });

  it("sends a message and displays response with citations", async () => {
    mockSendChatMessage.mockResolvedValue({
      reply: "Garbage is collected every Monday.",
      citations: [
        {
          title: "City Waste Policy",
          snippet: "Garbage is collected weekly in South C...",
          source_link: "https://example.com/policy",
        },
      ],
      confidence: 0.95,
    });

    render(<ChatInterface />);
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    await userEvent.type(input, "When is garbage collected?");
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText("When is garbage collected?")).toBeInTheDocument();
      expect(screen.getByText("Garbage is collected every Monday.")).toBeInTheDocument();
      expect(screen.getByText("City Waste Policy")).toBeInTheDocument();
      expect(screen.getByText("Garbage is collected weekly in South C...")).toBeInTheDocument();
      const sourceLink = screen.getByText("[Source]");
      expect(sourceLink).toHaveAttribute("href", "https://example.com/policy");
    });
  });

  it("handles empty input gracefully", async () => {
    render(<ChatInterface />);
    const sendButton = screen.getByRole("button", { name: /send/i });

    fireEvent.click(sendButton);

    expect(mockSendChatMessage).not.toHaveBeenCalled();
  });

  it("displays error message on API failure", async () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    mockSendChatMessage.mockRejectedValue(new Error("API error"));

    render(<ChatInterface />);
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    await userEvent.type(input, "Test error");
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/❌ Error talking to server/i)).toBeInTheDocument();
    });

    vi.spyOn(console, "error").mockRestore();
  });

  it("clears input after sending", async () => {
    mockSendChatMessage.mockResolvedValue({
      reply: "Test response",
      citations: [],
      confidence: 0.9,
    });

    render(<ChatInterface />);
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    await userEvent.type(input, "Test message");
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(input).toHaveValue("");
    });
  });

  it("handles missing citations gracefully", async () => {
    mockSendChatMessage.mockResolvedValue({
      reply: "No citations response",
      citations: [],
      confidence: 0.9,
    });

    render(<ChatInterface />);
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    await userEvent.type(input, "No citations");
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText("No citations response")).toBeInTheDocument();
      expect(screen.queryByText(/\[source\]/i)).not.toBeInTheDocument();
    });
  });

  it("offers incident form choice when intent is incident_report", async () => {
    mockSendChatMessage.mockResolvedValue({
      reply: "Let's file an incident.",
      intent: "incident_report",
      citations: [],
      confidence: 0.9,
    });

    render(<ChatInterface />);
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    await userEvent.type(input, "Report issue");
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/would you like to file this incident/i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /file in chat/i })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /open form/i })).toBeInTheDocument();
    });
  });
});
