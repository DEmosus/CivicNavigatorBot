import { useState } from "react";
import { isStaff, login, logout } from "../utils/auth";

export default function LoginForm({ onLogin }: { onLogin?: () => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);
    setSuccess(false);
    setLoading(true);
    try {
      await login(email, password);
      setEmail("");
      setPassword("");
      setSuccess(true);
      onLogin?.();
    } catch (e: unknown) {
      if (e instanceof Error) {
        try {
          const parsed = JSON.parse(e.message);
          setErr(parsed.detail || "Login failed");
        } catch {
          setErr(e.message || "Login failed");
        }
      } else {
        setErr("Login failed");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="p-4 border rounded bg-panel text-textPrimary"
      aria-label="Staff login form"
    >
      <h3 className="font-semibold mb-2">Staff Login</h3>

      {err && (
        <p className="text-error mb-2" role="alert">
          {err}
        </p>
      )}
      {success && (
        <p className="text-success mb-2" role="status">
          ✅ Logged in successfully
        </p>
      )}

      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="email"
        className="w-full mb-2 p-2 bg-panel border border-divider rounded text-white placeholder-gray-400 focus:outline-none focus:border-accentCyan"
        type="email"
        required
        aria-invalid={!!err}
      />
      <input
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="password"
        type="password"
        className="w-full mb-2 p-2 bg-panel border border-divider rounded text-white placeholder-gray-400 focus:outline-none focus:border-accentCyan"
        required
        aria-invalid={!!err}
      />

      <div className="flex gap-2">
        <button
          type="submit"
          className="bg-accentPink text-white p-2 rounded"
          disabled={loading}
        >
          {loading ? "Logging in..." : "Login"}
        </button>
        {isStaff() && (
          <button
            type="button"
            className="bg-panel p-2 rounded"
            onClick={() => {
              logout();
              onLogin?.();
            }}
          >
            Logout
          </button>
        )}
      </div>
    </form>
  );
}
