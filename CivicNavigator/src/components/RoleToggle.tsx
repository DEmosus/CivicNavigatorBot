type Role = "resident" | "staff";

interface RoleToggleProps {
  role: Role;
  onChange: (role: Role) => void;
}

const isRole = (value: string): value is Role =>
  value === "resident" || value === "staff";

export default function RoleToggle({ role, onChange }: RoleToggleProps) {
  return (
    <div className="mb-6 text-center">
      <label
        htmlFor="role"
        id="role-label"
        className="text-textPrimary text-sm font-medium mr-2"
      >
        Role:
      </label>
      <select
        id="role"
        aria-labelledby="role-label"
        value={role}
        onChange={(e) => {
          const value = e.target.value;
          if (isRole(value)) onChange(value);
        }}
        className="bg-midnight text-textPrimary border border-divider rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accentCyan transition"
      >
        <option value="resident">Resident</option>
        <option value="staff">Staff</option>
      </select>
    </div>
  );
}
