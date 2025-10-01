import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import type { ChatResponse } from "../types";
import { sendChatMessage } from "../utils/api";
import ChatInterface from "./ChatInterface";

// Mock the API call
vi.mock("../utils/api", () => ({
  sendChatMessage: vi.fn(),
}));

const mockSendChatMessage = vi.mocked(sendChatMessage);
type ChatResponseWithIntent = ChatResponse & { intent?: string };

beforeAll(() => {
  HTMLElement.prototype.scrollIntoView = vi.fn();
});

describe("ChatInterface", () => {
  beforeEach(() => {
    mockSendChatMessage.mockReset();
    localStorage.clear();
  });

  it("renders input and send button", () => {
    render(<ChatInterface role="resident" />);
    expect(
      screen.getByPlaceholderText(/type your message/i)
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /send/i })).toBeInTheDocument();
  });

  it("sends a message and displays response with citations", async () => {
    mockSendChatMessage.mockResolvedValue({
      session_id: "test-session",
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

    render(<ChatInterface role="resident" />);
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    await userEvent.type(input, "When is garbage collected?");
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(
        screen.getByText("When is garbage collected?")
      ).toBeInTheDocument();
      expect(
        screen.getByText("Garbage is collected every Monday.")
      ).toBeInTheDocument();

      // Match actual rendered text with prefix
      expect(
        screen.getByText(
          /city waste policy: garbage is collected weekly in south c/i
        )
      ).toBeInTheDocument();
    });
  });

  it("handles empty input gracefully", async () => {
    render(<ChatInterface role="resident" />);
    const sendButton = screen.getByRole("button", { name: /send/i });

    fireEvent.click(sendButton);

    expect(mockSendChatMessage).not.toHaveBeenCalled();
  });

  it("displays error message on API failure", async () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    mockSendChatMessage.mockRejectedValue(new Error("API error"));

    render(<ChatInterface role="resident" />);
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    await userEvent.type(input, "Test error");
    fireEvent.click(sendButton);

    await waitFor(() => {
      // Match actual error text
      expect(
        screen.getByText(/❌ sorry, something went wrong/i)
      ).toBeInTheDocument();
    });

    vi.spyOn(console, "error").mockRestore();
  });

  it("clears input after sending", async () => {
    mockSendChatMessage.mockResolvedValue({
      session_id: "test-session",
      reply: "Test response",
      citations: [],
      confidence: 0.9,
    });

    render(<ChatInterface role="resident" />);
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
      session_id: "test-session",
      reply: "No citations response",
      citations: [],
      confidence: 0.9,
    });

    render(<ChatInterface role="resident" />);
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    await userEvent.type(input, "No citations");
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText("No citations response")).toBeInTheDocument();
      expect(screen.queryByText(/\[Source\]/i)).not.toBeInTheDocument();
    });
  });

  it("offers incident form choice when intent is incident_report", async () => {
    mockSendChatMessage.mockResolvedValue({
      session_id: "test-session",
      reply: "Let's file an incident.",
      intent: "incident_report",
      citations: [],
      confidence: 0.9,
    } as ChatResponseWithIntent);

    render(<ChatInterface role="resident" />);
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    await userEvent.type(input, "Report issue");
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/let's file an incident/i)).toBeInTheDocument();
    });
  });
});
