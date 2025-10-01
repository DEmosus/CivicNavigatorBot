import type {
  ChatResponse,
  IncidentCreated,
  IncidentFormData,
  IncidentStatusResponse,
  KBSearchOut,
  KBSearchResponse,
  StaffIncidentListItem,
  TokenOut,
} from "../types";
import { getToken } from "./auth";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

/** helper for GET */
async function getJSON<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...((opts.headers as Record<string, string>) || {}),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { ...opts, headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return (await res.json()) as T;
}

/** helper for POST */
async function postJSON<T>(
  path: string,
  body: unknown,
  opts: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((opts.headers as Record<string, string>) || {}),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    body: JSON.stringify(body),
    ...opts,
    headers,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return (await res.json()) as T;
}

/** helper for PATCH */
async function patchJSON<T>(
  path: string,
  body: unknown,
  opts: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((opts.headers as Record<string, string>) || {}),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, {
    method: "PATCH",
    body: JSON.stringify(body),
    ...opts,
    headers,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return (await res.json()) as T;
}

/** --- API FUNCTIONS --- */

/** Chat */
export async function sendChatMessage(
  message: string,
  role: string,
  session_id?: string
): Promise<ChatResponse> {
  return postJSON<ChatResponse>("/api/chat/message", {
    message,
    role,
    session_id: session_id || crypto.randomUUID(),
  });
}

/** Create incident */
export async function createIncident(
  data: IncidentFormData
): Promise<IncidentCreated> {
  return postJSON<IncidentCreated>("/api/incidents", data);
}

/** Get incident status */
export async function getIncidentStatus(
  id: string
): Promise<IncidentStatusResponse> {
  return getJSON<IncidentStatusResponse>(`/api/incidents/${id}/status`);
}

/** Public KB search */
export async function searchPublicKb(query: string): Promise<KBSearchResponse> {
  return getJSON<KBSearchResponse>(
    `/api/kb/search?q=${encodeURIComponent(query)}`
  );
}

/** Staff KB search */
export async function searchStaffKb(query: string): Promise<KBSearchOut> {
  return getJSON<KBSearchOut>(
    `/api/staff/kb/search?query=${encodeURIComponent(query)}`
  );
}

/** Staff: get all incidents */
export async function getAllIncidents(): Promise<StaffIncidentListItem[]> {
  return getJSON<StaffIncidentListItem[]>("/api/staff/incidents");
}

/** Staff: update incident status (with optional note) */
export async function updateIncidentStatus(
  incidentId: string,
  status: string,
  note?: string
): Promise<{ incident_id: string; status: string; last_update: string }> {
  return patchJSON(`/api/staff/incidents/${incidentId}`, { status, note });
}

/** Auth: register new user */
export async function registerUser(
  email: string,
  password: string,
  full_name = "",
  is_staff = false
): Promise<TokenOut> {
  return postJSON<TokenOut>("/api/auth/register", {
    email,
    password,
    full_name,
    is_staff,
  });
}

/** Auth: login user */
export async function loginUser(
  email: string,
  password: string
): Promise<TokenOut> {
  return postJSON<TokenOut>("/api/auth/login", { email, password });
}
