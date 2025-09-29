import { loginUser } from "./api";

export function getToken(): string | null {
  return localStorage.getItem("civic_token");
}

export function isStaff(): boolean {
  return localStorage.getItem("is_staff") === "true";
}

export async function login(email: string, password: string) {
  const data = await loginUser(email, password);
  localStorage.setItem("civic_token", data.access_token);
  localStorage.setItem("is_staff", String(Boolean(data.is_staff)));
}

export function logout() {
  localStorage.removeItem("civic_token");
  localStorage.removeItem("is_staff");
}
