import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./features/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    // Frozen breakpoints — standard Tailwind (sm, md, lg, xl, 2xl). No custom additions.
    extend: {
      colors: {
        // All color tokens reference CSS variables so they respond to .dark
        background: "var(--background)",
        foreground: "var(--foreground)",
        surface:    "var(--surface)",
        border:     "var(--border)",
        muted:      "var(--muted)",
        brand: {
          50:  "var(--brand-50)",
          100: "var(--brand-100)",
          200: "var(--brand-200)",
          500: "var(--brand-500)",
          600: "var(--brand-600)",
          700: "var(--brand-700)",
          900: "var(--brand-900)",
        },
        success: "var(--success)",
        warning: "var(--warning)",
        danger:  "var(--danger)",
        info:    "var(--info)",
      },

      // Frozen spacing additions — all other spacing uses Tailwind defaults
      spacing: {
        "18":  "4.5rem",
        "22":  "5.5rem",
        "88":  "22rem",
        "128": "32rem",
      },

      // Frozen border-radius — use these names only, no ad-hoc rounded-* utilities
      borderRadius: {
        sm:   "0.25rem",   // 4px
        md:   "0.5rem",    // 8px
        lg:   "0.75rem",   // 12px
        xl:   "1rem",      // 16px
        full: "9999px",
      },

      // Frozen box-shadow
      boxShadow: {
        sm:   "0 2px 4px rgba(0,0,0,0.05)",
        md:   "0 4px 12px rgba(0,0,0,0.08)",
        lg:   "0 8px 24px rgba(0,0,0,0.15)",
        glow: "0 0 0 2px var(--brand-500), 0 0 12px rgba(59, 130, 246, 0.3)",
      },

      // Frozen z-index scale — never use z-[arbitrary] outside this registry
      zIndex: {
        sidebar: "40",
        topbar:  "50",
        modal:   "60",
        toast:   "70",
        overlay: "80",
      },

      // Frozen animation keyframes
      keyframes: {
        "fade-in": {
          "0%":   { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "slide-in": {
          "0%":   { transform: "translateY(-8px)", opacity: "0" },
          "100%": { transform: "translateY(0)",    opacity: "1" },
        },
        "pulse-soft": {
          "0%, 100%": { opacity: "1" },
          "50%":      { opacity: "0.5" },
        },
      },
      animation: {
        "fade-in":    "fade-in 0.15s ease-out",
        "slide-in":   "slide-in 0.2s ease-out",
        "pulse-soft": "pulse-soft 2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
