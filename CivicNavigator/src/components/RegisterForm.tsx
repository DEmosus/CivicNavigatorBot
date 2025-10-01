import { useState } from "react";
import type { ValidationErrorItem } from "../types";
import { registerUser } from "../utils/api";

export default function RegisterForm({
  onRegister,
}: {
  onRegister?: () => void;
}) {
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [isStaff, setIsStaff] = useState(false);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);
    setSuccessMsg(null);
    setLoading(true);

    try {
      const data = await registerUser(email, password, fullName, isStaff);

      if (data?.access_token) {
        localStorage.setItem("civic_token", data.access_token);
        localStorage.setItem(
          "is_staff",
          String(Boolean(data.is_staff || isStaff))
        );
        setSuccessMsg("✅ Registered and logged in.");
      } else {
        setSuccessMsg("✅ Registered successfully. Please log in.");
      }

      setEmail("");
      setFullName("");
      setPassword("");
      setIsStaff(false);

      onRegister?.();
    } catch (error: unknown) {
      if (error instanceof Error) {
        try {
          const parsed = JSON.parse(error.message);
          if (parsed?.detail) {
            if (Array.isArray(parsed.detail)) {
              const details = parsed.detail as ValidationErrorItem[];
              setErr(details.map((d) => d.msg).join(", "));
            } else {
              setErr(String(parsed.detail));
            }
          } else {
            setErr(String(parsed));
          }
        } catch {
          setErr(error.message);
        }
      } else {
        setErr("❌ Registration failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="p-4 border rounded bg-panel text-textPrimary"
      aria-label="Register Form"
    >
      <h3 className="font-semibold mb-3">Register</h3>

      {err && (
        <p id="register-error" className="text-error mb-2" role="alert">
          {err}
        </p>
      )}
      {successMsg && (
        <p className="text-success mb-2" role="status">
          {successMsg}
        </p>
      )}

      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email address"
        type="email"
        required
        aria-invalid={!!err}
        className="w-full mb-2 p-2 bg-midnight border border-divider rounded text-textPrimary placeholder:text-textMuted focus:outline-none focus:border-accentCyan"
      />

      <input
        value={fullName}
        onChange={(e) => setFullName(e.target.value)}
        placeholder="Full name (optional)"
        className="w-full mb-2 p-2 bg-midnight border border-divider rounded text-textPrimary placeholder:text-textMuted focus:outline-none focus:border-accentCyan"
      />

      <input
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        type="password"
        required
        className="w-full mb-2 p-2 bg-midnight border border-divider rounded text-textPrimary placeholder:text-textMuted focus:outline-none focus:border-accentCyan"
      />

      <label className="flex items-center gap-2 mb-3">
        <input
          type="checkbox"
          checked={isStaff}
          onChange={(e) => setIsStaff(e.target.checked)}
          aria-label="Register as staff"
        />
        <span>Register as staff</span>
      </label>

      <button
        type="submit"
        className="bg-accentPink hover:bg-pink-500 text-white px-4 py-2 rounded w-full"
        disabled={loading}
      >
        {loading ? "Registering..." : "Register"}
      </button>
    </form>
  );
}
