interface RoleToggleProps {
  role: "resident" | "staff";
  onChange: (role: "resident" | "staff") => void;
}

export default function RoleToggle({ role, onChange }: RoleToggleProps) {
  return (
    <div className="mb-6 text-center">
      <label htmlFor="role" className="text-textPrimary text-sm font-medium mr-2">
        Role:
      </label>
      <select
        id="role"
        value={role}
        onChange={(e) => onChange(e.target.value as "resident" | "staff")}
        className="bg-midnight text-textPrimary border border-divider rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accentCyan transition"
      >
        <option value="resident">Resident</option>
        <option value="staff">Staff</option>
      </select>
    </div>
  );
}
