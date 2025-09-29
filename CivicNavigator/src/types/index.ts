export interface Citation {
  title: string;
  snippet: string;
  source_link?: string;
}

/** Raw chat message returned by backend */
export interface ChatMessage {
  user: string;
  bot: string;
  citations: Citation[];
  confidence: number;
}

/** Data used to create a new incident */
export interface IncidentFormData {
  title?: string;
  description?: string;
  category?: string;
  location_text?: string;
  contact_email?: string;
  priority?: "low" | "medium" | "high";
  [key: string]: unknown;
}

/** Response when checking incident status */
export interface IncidentStatusResponse {
  incident_id: string;
  status: string;
  last_update?: string;
  history: {
    status: string;
    timestamp: string;
    note?: string;
  }[];
}

/** Response from chatbot API */
export interface ChatResponse {
  reply: string;
  citations?: Citation[];
  intent?: "incident_report" | "status_check" | "general";
  confidence?: number;
  incident_id?: string;
  session_id?: string;
}

/** Local chat UI message (different from backend ChatMessage) */
export interface Message {
  id: string;
  role: "user" | "bot" | "system";
  text: string;
  buttons?: { label: string; action: () => void }[];
}
