/** Citation object returned by backend */
export interface Citation {
  title: string;
  snippet: string;
  source_link?: string | null;
}

/** Raw chat message returned by backend */
export interface ChatMessage {
  user: string;
  bot: string;
  citations: Citation[];
  confidence: number;
}

/** Allowed incident categories (IncidentCategory enum) */
export type IncidentCategory =
  | "road_maintenance"
  | "waste_management"
  | "water_supply"
  | "electricity"
  | "street_lighting"
  | "drainage"
  | "other";

/** Data used to create a new incident (matches IncidentCreate) */
export interface IncidentFormData {
  title: string;
  description: string;
  category?: IncidentCategory;
  location_text?: string | null;
  contact_email?: string | null;
}

/** Response when creating a new incident (IncidentCreated) */
export interface IncidentCreated {
  incident_id: string;
  status: string;
  created_at: string; // ISO datetime
}

/** Response when checking incident status (IncidentStatusOut) */
export interface IncidentStatusResponse {
  status: string;
  last_update: string; // ISO datetime
  history: {
    note: string;
    status: string;
    timestamp: string; // ISO datetime
  }[];
}

/** Response from chatbot API (ChatOut) */
export interface ChatResponse {
  reply: string;
  citations?: Citation[];
  confidence?: number;
  session_id: string;
}

/** Local chat UI message (frontend only) */
export interface Message {
  id: string;
  role: "user" | "bot" | "system";
  text: string;
  buttons?: { label: string; action: () => void }[];
}

/** Staff incident list item (StaffIncidentListItem) */
export interface StaffIncidentListItem {
  incident_id: string;
  title?: string | null;
  category?: string | null;
  priority?: string | null;
  description?: string | null;
  status: string;
  created_at?: string | null;
  last_update: string;
}

/** Staff incident update input (StaffIncidentUpdateIn) */
export interface StaffIncidentUpdate {
  status: string;
  note?: string | null;
}

/** Auth token response (TokenOut) */
export interface TokenOut {
  access_token: string;
  token_type?: string;
  is_staff: boolean;
}

/** KB search result (staff KBSearchOut) */
export interface KBSearchResultItem {
  doc_id: string;
  title: string;
  snippet: string;
  score: number;
  source_url?: string | null;
}

export interface KBSearchOut {
  results: KBSearchResultItem[];
}

/** Public KB entry (KBEntry) */
export interface KBEntry {
  id?: number | null;
  question: string;
  answer: string;
}

export interface KBSearchResponse {
  results: KBEntry[];
}

export interface ValidationErrorItem {
  loc: (string | number)[];
  msg: string;
  type: string;
}
