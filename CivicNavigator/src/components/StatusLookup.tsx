import { useState } from "react";
import { getIncidentStatus } from "../utils/api";

interface IncidentStatus {
  status: string;
  last_update: string;
  history: { note: string; timestamp: string }[];
}

export default function StatusLookup() {
  const [input, setInput] = useState("");
  const [incident, setIncident] = useState<IncidentStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) {
      setError("⚠️ Please enter an incident ID.");
      setIncident(null);
      return;
    }
    setIsLoading(true);
    try {
      const data = await getIncidentStatus(input.trim());
      setIncident(data);
      setError("");
    } catch {
      setError("⚠️ Incident not found.");
      setIncident(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-panel border border-divider text-textPrimary rounded-xl p-4 mb-6 shadow">
      <h2 className="text-2xl font-semibold mb-4">Check Incident Status</h2>
      <form onSubmit={handleSubmit} className="flex flex-wrap gap-2 sm:flex-nowrap mb-4" aria-label="Check Incident Status">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-grow bg-midnight border border-divider text-textPrimary p-2 rounded-l"
          placeholder="Enter Incident ID"
          aria-label="incident id"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="bg-accentCyan hover:bg-cyan-400 text-midnight px-4 py-2 rounded-r"
        >
          {isLoading ? "Checking..." : "Check"}
        </button>
      </form>

      {error && <p className="text-error text-sm">{error}</p>}

      {incident && (
        <div className="text-sm text-textMuted">
          <p>
            <strong>Status:</strong> {incident.status}
          </p>
          <p>
            <strong>Last Updated:</strong> {incident.last_update}
          </p>
          <ul className="list-disc ml-6 mt-2">
            {incident.history.map((h, i) => (
              <li key={i}>
                {h.note} ({h.timestamp})
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}