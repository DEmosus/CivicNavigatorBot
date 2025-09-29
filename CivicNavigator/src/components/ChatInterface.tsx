import { useEffect, useRef, useState } from "react";
import type {
  ChatResponse,
  IncidentFormData,
  IncidentStatusResponse,
  Message,
} from "../types";
import {
  createIncident,
  getIncidentStatus,
  sendChatMessage,
} from "../utils/api";

type IncidentStep =
  | "idle"
  | "awaiting_title"
  | "awaiting_category"
  | "awaiting_location"
  | "awaiting_email"
  | "awaiting_description"
  | "review";

const initialIncident: IncidentFormData = {
  title: "",
  category: "",
  location_text: "",
  contact_email: "",
  description: "",
};

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string>(() => {
    return localStorage.getItem("civic_session_id") || crypto.randomUUID();
  });
  const [incidentStep, setIncidentStep] = useState<IncidentStep>("idle");
  const [incidentData, setIncidentData] =
    useState<IncidentFormData>(initialIncident);

  const chatEndRef = useRef<HTMLDivElement | null>(null);

  /** 🔄 Scroll to bottom on new message */
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /** 💾 Load persisted messages on mount */
  useEffect(() => {
    const savedMessages = localStorage.getItem("civic_messages");
    if (savedMessages) {
      try {
        setMessages(JSON.parse(savedMessages));
      } catch (err) {
        console.warn("Failed to parse saved messages:", err);
      }
    }
  }, []);

  /** 💾 Save session + messages whenever they change */
  useEffect(() => {
    localStorage.setItem("civic_session_id", sessionId);
    localStorage.setItem("civic_messages", JSON.stringify(messages));
  }, [sessionId, messages]);

  const addMessage = (
    role: "user" | "bot" | "system",
    text: string,
    buttons?: Message["buttons"]
  ) => {
    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role, text, buttons },
    ]);
  };

  /** 📝 Validation helpers */
  const validateEmail = (email: string): boolean =>
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  const validateCategory = (category: string): boolean => {
    const allowed = ["road_maintenance", "waste_management", "water", "other"];
    return allowed.includes(category.toLowerCase());
  };

  /** 📝 Handle guided incident flow */
  const handleIncidentStep = async (userInput: string) => {
    switch (incidentStep) {
      case "awaiting_title": {
        if (!userInput.trim()) {
          addMessage("bot", "⚠️ Title cannot be empty. Please provide one.");
          return;
        }
        setIncidentData((prev) => ({ ...prev, title: userInput }));
        setIncidentStep("awaiting_category");
        addMessage(
          "bot",
          "What category best describes this issue? (road_maintenance, waste_management, water, other)"
        );
        return;
      }
      case "awaiting_category": {
        if (!validateCategory(userInput)) {
          addMessage(
            "bot",
            "⚠️ Invalid category. Please choose: road_maintenance, waste_management, water, or other."
          );
          return;
        }
        setIncidentData((prev) => ({ ...prev, category: userInput }));
        setIncidentStep("awaiting_location");
        addMessage(
          "bot",
          "Where is this incident located? (landmark or address)"
        );
        return;
      }
      case "awaiting_location": {
        if (!userInput.trim()) {
          addMessage("bot", "⚠️ Location cannot be empty. Please provide one.");
          return;
        }
        setIncidentData((prev) => ({ ...prev, location_text: userInput }));
        setIncidentStep("awaiting_email");
        addMessage("bot", "Please provide your contact email.");
        return;
      }
      case "awaiting_email": {
        if (!validateEmail(userInput)) {
          addMessage("bot", "⚠️ Invalid email format. Please try again.");
          return;
        }
        setIncidentData((prev) => ({ ...prev, contact_email: userInput }));
        setIncidentStep("awaiting_description");
        addMessage("bot", "Please describe the incident in detail.");
        return;
      }
      case "awaiting_description": {
        if (!userInput.trim()) {
          addMessage("bot", "⚠️ Description cannot be empty.");
          return;
        }
        const finalData = { ...incidentData, description: userInput };
        setIncidentData(finalData);
        setIncidentStep("review");
        addMessage(
          "bot",
          `Here’s what I got:\n- Title: ${finalData.title}\n- Category: ${finalData.category}\n- Location: ${finalData.location_text}\n- Email: ${finalData.contact_email}\n- Description: ${finalData.description}\n\nSubmit this incident?`,
          [
            {
              label: "✅ Submit",
              action: async () => {
                try {
                  const res = await createIncident(finalData);
                  addMessage(
                    "bot",
                    `✅ Incident submitted successfully! Reference ID: ${res.incident_id}`
                  );
                  setIncidentStep("idle");
                  setIncidentData(initialIncident);
                } catch (err) {
                  console.error("Submit error:", err);
                  addMessage(
                    "bot",
                    "❌ Failed to submit incident. Please try again."
                  );
                }
              },
            },
            {
              label: "✏️ Edit",
              action: () => {
                setIncidentStep("awaiting_title");
                addMessage(
                  "bot",
                  "Okay, let’s start again. What is the title?"
                );
              },
            },
          ]
        );
        return;
      }
      default:
        return;
    }
  };

  /** 📩 Handle sending user input */
  const handleSend = async () => {
    if (!input.trim()) return;
    const userText = input.trim();

    addMessage("user", userText);
    setInput("");

    // Guided flow
    if (incidentStep !== "idle") {
      await handleIncidentStep(userText);
      return;
    }

    try {
      const response: ChatResponse = await sendChatMessage(
        userText,
        "resident",
        sessionId
      );
      addMessage("bot", response.reply);

      if (response.intent === "incident_report") {
        // Start guided flow
        setIncidentStep("awaiting_title");
        addMessage("bot", "Let’s file an incident. What is the title?");
        return;
      }

      if (response.intent === "status_check" && response.incident_id) {
        addMessage(
          "bot",
          `🔎 Checking status for incident ${response.incident_id}...`
        );

        try {
          const status: IncidentStatusResponse = await getIncidentStatus(
            response.incident_id
          );
          const historyLines = status.history
            .map(
              (h) =>
                `- ${h.status} (${new Date(h.timestamp).toLocaleString()})${
                  h.note ? ` — ${h.note}` : ""
                }`
            )
            .join("\n");

          addMessage(
            "bot",
            `📋 Incident ${status.incident_id} is currently *${status.status}*.\n\nHistory:\n${historyLines}`
          );
        } catch (err) {
          console.error("Status check error:", err);
          addMessage("bot", "❌ Failed to retrieve status. Please try again.");
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      addMessage("bot", "❌ Sorry, something went wrong.");
    }
  };

  /** 🔄 Reset chat + clear persistence */
  const handleNewChat = () => {
    setMessages([]);
    setIncidentStep("idle");
    setIncidentData(initialIncident);
    const newSession = crypto.randomUUID();
    setSessionId(newSession);
    localStorage.removeItem("civic_messages");
    localStorage.setItem("civic_session_id", newSession);
    addMessage("bot", "👋 New chat started. How can I help you?");
  };

  return (
    <div className="flex flex-col h-full bg-midnight text-textPrimary rounded-xl shadow-lg">
      {/* Header with reset button */}
      <div className="flex justify-between items-center p-3 border-b border-divider bg-panel">
        <h2 className="font-bold">CivicNavigator</h2>
        <button
          onClick={handleNewChat}
          className="text-sm bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded"
        >
          New Chat
        </button>
      </div>

      {/* Chat window */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-xs px-4 py-2 rounded-lg shadow ${
                msg.role === "user"
                  ? "bg-accentPink text-white"
                  : "bg-panel text-textPrimary"
              }`}
            >
              <p className="whitespace-pre-line">{msg.text}</p>
              {msg.buttons && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {msg.buttons.map((btn, idx) => (
                    <button
                      key={idx}
                      onClick={btn.action}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
                    >
                      {btn.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t border-divider flex">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type your message..."
          className="flex-1 bg-panel border border-divider rounded px-3 py-2 text-textPrimary"
        />
        <button
          onClick={handleSend}
          className="ml-2 bg-accentPink hover:bg-pink-500 text-white px-4 py-2 rounded"
        >
          Send
        </button>
      </div>
    </div>
  );
}
