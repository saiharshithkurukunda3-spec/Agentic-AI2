/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          dark: "#0a0a0f",
          card: "#12121e",
          border: "#1f1f35",
          accent: "#6366f1", // Indigo
          accentLight: "#818cf8",
          glow: "#3b82f6", // Blue
          cyan: "#22d3ee" // Cyan
        }
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow-spin': 'glow-spin 1.5s ease-in-out infinite',
      },
      keyframes: {
        'glow-spin': {
          '0%, 100%': { transform: 'scale(1)', opacity: 0.5 },
          '50%': { transform: 'scale(1.05)', opacity: 0.8 },
        }
      }
    },
  },
  plugins: [],
}
