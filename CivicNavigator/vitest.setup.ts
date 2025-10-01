import "@testing-library/jest-dom";
import { vi } from "vitest";

// ✅ Mock scrollIntoView so jsdom doesn’t crash
if (!HTMLElement.prototype.scrollIntoView) {
  HTMLElement.prototype.scrollIntoView = vi.fn();
}

// ✅ Mock matchMedia (used by some UI libs, Tailwind, etc.)
if (!window.matchMedia) {
  window.matchMedia = vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }));
}

// ✅ Mock ResizeObserver (used by charts, layout libs, etc.)
if (!window.ResizeObserver) {
  window.ResizeObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }));
}
