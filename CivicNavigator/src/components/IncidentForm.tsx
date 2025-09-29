import { useEffect, useRef, useState } from "react";
import type { IncidentFormData } from "../types";
import { createIncident } from "../utils/api";

interface ValidationError {
  [key: string]: string;
}

interface PydanticErrorItem {
  loc?: [string, string] | string[];
  msg: string;
}

interface APIErrorResponse {
  status: number;
  data?: PydanticErrorItem[] | { detail?: string };
}

interface APIError {
  response?: APIErrorResponse;
}

const initialForm: IncidentFormData = {
  title: "",
  description: "",
  category: "",
  location_text: "",
  contact_email: "",
  priority: "medium",
};

const CATEGORY_OPTIONS = [
  "road_maintenance",
  "waste_management",
  "water_supply",
  "electricity",
  "street_lighting",
  "drainage",
  "other",
];

const PRIORITY_OPTIONS = ["low", "medium", "high"];

interface IncidentFormProps {
  onSubmitted?: (id: string) => void;
  prefill?: Partial<IncidentFormData>;
}

export default function IncidentForm({
  onSubmitted,
  prefill,
}: IncidentFormProps) {
  const [formData, setFormData] = useState(initialForm);
  const [errors, setErrors] = useState<ValidationError>({});
  const [isLoading, setIsLoading] = useState(false);
  const [incidentId, setIncidentId] = useState<string | null>(null);
  const errorRef = useRef<HTMLParagraphElement | null>(null);
  const successRef = useRef<HTMLParagraphElement | null>(null);

  useEffect(() => {
    if (prefill) {
      setFormData((prev) => ({ ...prev, ...prefill }));
    }
  }, [prefill]);

  const validateForm = (): boolean => {
    const newErrors: ValidationError = {};

    if (!formData.title.trim() || formData.title.length < 3) {
      newErrors.title = "Title must be at least 3 characters.";
    }
    if (!formData.description.trim() || formData.description.length < 10) {
      newErrors.description = "Description must be at least 10 characters.";
    }
    if (!formData.category) {
      newErrors.category = "Please select a category.";
    }
    if (!formData.priority) {
      newErrors.priority = "Please select a priority.";
    }
    if (
      formData.contact_email &&
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.contact_email)
    ) {
      newErrors.contact_email = "Please enter a valid email address.";
    }

    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) {
      errorRef.current?.focus();
      return false;
    }
    return true;
  };

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setIncidentId(null);

    if (!validateForm()) return;

    setIsLoading(true);

    try {
      const payload = {
        ...formData,
        location_text: formData.location_text || undefined,
      };

      const response = await createIncident(payload);
      setIncidentId(response.incident_id);
      setFormData(initialForm); // reset after submit

      // ✅ Notify ChatInterface if provided
      if (onSubmitted) {
        onSubmitted(response.incident_id);
      } else {
        successRef.current?.focus();
      }
    } catch (err: unknown) {
      const errorObj = err as APIError;
      if (errorObj.response?.status === 422) {
        const errResponse = errorObj.response;
        if (Array.isArray(errResponse.data)) {
          const fieldErrors: ValidationError = {};
          (errResponse.data as PydanticErrorItem[]).forEach((e) => {
            const field = (Array.isArray(e.loc) && e.loc[1]) || "general";
            fieldErrors[field] = e.msg;
          });
          setErrors(fieldErrors);
        } else if (
          errResponse.data &&
          "detail" in errResponse.data &&
          errResponse.data.detail
        ) {
          setErrors({ general: errResponse.data.detail });
        }
      } else {
        setErrors({
          general: "❌ Failed to submit incident. Please try again.",
        });
      }
      errorRef.current?.focus();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-panel border border-divider text-textPrimary rounded-xl p-4 mb-6 shadow animate-fadeIn">
      <h2 className="text-2xl font-semibold mb-4">Report an Incident</h2>
      <form
        aria-label="Report Incident Form"
        onSubmit={handleSubmit}
        noValidate
      >
        {errors.general && (
          <p
            className="text-error mb-2"
            role="alert"
            tabIndex={-1}
            ref={errorRef}
          >
            {errors.general}
          </p>
        )}

        <input
          name="title"
          value={formData.title}
          onChange={handleChange}
          className="w-full bg-midnight border border-divider text-textPrimary p-2 mb-1 rounded"
          placeholder="Title"
          aria-label="Incident title"
          required
        />
        {errors.title && <p className="text-error mb-2">{errors.title}</p>}

        <select
          name="category"
          value={formData.category}
          onChange={handleChange}
          className="w-full bg-midnight border border-divider text-textPrimary p-2 mb-1 rounded"
          aria-label="Incident category"
          required
        >
          <option value="">Select category</option>
          {CATEGORY_OPTIONS.map((cat) => (
            <option key={cat} value={cat}>
              {cat.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
            </option>
          ))}
        </select>
        {errors.category && (
          <p className="text-error mb-2">{errors.category}</p>
        )}

        <select
          name="priority"
          value={formData.priority}
          onChange={handleChange}
          className="w-full bg-midnight border border-divider text-textPrimary p-2 mb-1 rounded"
          aria-label="Incident priority"
          required
        >
          <option value="">Select priority</option>
          {PRIORITY_OPTIONS.map((p) => (
            <option key={p} value={p}>
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </option>
          ))}
        </select>
        {errors.priority && (
          <p className="text-error mb-2">{errors.priority}</p>
        )}

        <input
          name="location_text"
          value={formData.location_text}
          onChange={handleChange}
          className="w-full bg-midnight border border-divider text-textPrimary p-2 mb-1 rounded"
          placeholder="Location (landmark or address)"
          aria-label="Incident location"
        />
        {errors.location_text && (
          <p className="text-error mb-2">{errors.location_text}</p>
        )}

        <input
          name="contact_email"
          value={formData.contact_email}
          onChange={handleChange}
          className="w-full bg-midnight border border-divider text-textPrimary p-2 mb-1 rounded"
          placeholder="Contact email"
          aria-label="Contact email"
          type="email"
        />
        {errors.contact_email && (
          <p className="text-error mb-2">{errors.contact_email}</p>
        )}

        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          className="w-full bg-midnight border border-divider text-textPrimary p-2 mb-1 rounded"
          placeholder="Description"
          aria-label="Incident description"
          required
        />
        {errors.description && (
          <p className="text-error mb-2">{errors.description}</p>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="flex items-center justify-center gap-2 bg-accentPink hover:bg-pink-500 text-white px-4 py-2 rounded transition-colors"
        >
          {isLoading && (
            <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          )}
          {isLoading ? "Submitting..." : "Submit Incident"}
        </button>
      </form>

      {incidentId && !onSubmitted && (
        <p
          className="mt-2 text-sm text-success"
          role="status"
          tabIndex={-1}
          ref={successRef}
        >
          ✅ Incident submitted successfully! Reference ID:{" "}
          <strong>{incidentId}</strong>
        </p>
      )}
    </div>
  );
}
