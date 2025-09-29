/** @type {import('tailwindcss').Config} */
// tailwind.config.ts
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        midnight: '#0D1B2A',       // page background
        panel: '#1A1D24',          // cards / sections
        textPrimary: '#F0F0F0',    // main text
        textMuted: '#9CA3AF',      // secondary text
        accentPink: '#FF4081',     // buttons, active
        accentCyan: '#22D3EE',     // links, icons
        accentGreen: '#00E676',    // success (optional)
        success: '#34D399',        // confirmations
        error: '#F87171',          // validation
        divider: '#2C3E50',        // borders
      },
    },
  },
  plugins: [],
};



