import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        space: {
          900: "#0B1020",
          800: "#0E1526",
          700: "#141B34",
          600: "#1A2340",
          500: "#22305C",
          400: "#2D3D6B",
          300: "#3B4F82",
        },
        primary: {
          50:  "#F5F3FF",
          100: "#EDE9FE",
          200: "#DDD6FE",
          300: "#C4B5FD",
          400: "#A78BFA",
          500: "#8B5CF6",
          600: "#7C3AED",
          700: "#6D28D9",
          800: "#5B21B6",
          900: "#4C1D95",
        },
        accent: {
          50:  "#F0F9FF",
          100: "#E0F2FE",
          200: "#BAE6FD",
          300: "#7DD3FC",
          400: "#38BDF8",
          500: "#0EA5E9",
          600: "#0284C7",
          700: "#0369A1",
        },
        status: {
          available: "#22C55E",
          busy:      "#EF4444",
          away:      "#F59E0B",
          offline:   "#475569",
        },
        text: {
          primary:   "#F8FAFC",
          secondary: "#CBD5E1",
          muted:     "#64748B",
          inverse:   "#0B1020",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
        mono: ["JetBrains Mono", "SF Mono", "Fira Code", "monospace"],
      },
      boxShadow: {
        "glow-sm":   "0 0 8px rgba(139, 92, 246, 0.6)",
        "glow-md":   "0 0 16px rgba(139, 92, 246, 0.6)",
        "glow-lg":   "0 0 32px rgba(139, 92, 246, 0.6)",
        "glow-available": "0 0 12px rgba(34, 197, 94, 0.5)",
        "glow-connect":   "0 0 20px rgba(56, 189, 248, 0.5)",
      },
      animation: {
        "fade-in":       "fadeIn 0.2s ease-out",
        "slide-up":      "slideUp 0.3s ease-out",
        "scale-in":      "scaleIn 0.2s cubic-bezier(0.34, 1.56, 0.64, 1)",
        "shimmer":       "shimmer 1.5s ease-in-out infinite",
        "pulse-glow":    "pulseGlow 2s ease-in-out infinite",
        "twinkle":       "twinkle 3s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          from: { opacity: "0" },
          to:   { opacity: "1" },
        },
        slideUp: {
          from: { opacity: "0", transform: "translateY(8px)" },
          to:   { opacity: "1", transform: "translateY(0)" },
        },
        scaleIn: {
          from: { opacity: "0", transform: "scale(0.95)" },
          to:   { opacity: "1", transform: "scale(1)" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        pulseGlow: {
          "0%, 100%": { boxShadow: "0 0 8px rgba(34, 197, 94, 0.5)" },
          "50%":      { boxShadow: "0 0 20px rgba(34, 197, 94, 0.5), 0 0 40px rgba(34, 197, 94, 0.3)" },
        },
        twinkle: {
          "0%, 100%": { opacity: "0.6", transform: "scale(0.9)" },
          "50%":      { opacity: "1", transform: "scale(1.1)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
