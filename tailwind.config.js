/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "rgb(var(--c-bg) / <alpha-value>)",
        card: "rgb(var(--c-card) / <alpha-value>)",
        "card-hover": "rgb(var(--c-card-hover) / <alpha-value>)",
        accent: "rgb(var(--c-accent) / <alpha-value>)",
        "accent-dark": "rgb(var(--c-accent-dark) / <alpha-value>)",
        "high-risk": "rgb(var(--c-high-risk) / <alpha-value>)",
        "medium-risk": "rgb(var(--c-medium-risk) / <alpha-value>)",
        safe: "rgb(var(--c-safe) / <alpha-value>)",
        "text-primary": "rgb(var(--c-text-primary) / <alpha-value>)",
        "text-secondary": "rgb(var(--c-text-secondary) / <alpha-value>)",
        border: "rgb(var(--c-border) / <alpha-value>)",
      },
      fontFamily: {
        display: ["'Exo 2'", "sans-serif"],
        body: ["'DM Sans'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      boxShadow: {
        glow: "0 0 20px rgba(14,165,233,0.4)",
        "glow-lg": "0 0 40px rgba(14,165,233,0.5)",
        "glow-red": "0 0 20px rgba(239,68,68,0.5)",
        "glow-amber": "0 0 20px rgba(245,158,11,0.5)",
        "glow-green": "0 0 20px rgba(34,197,94,0.5)",
        depth: "0 25px 50px rgba(0,0,0,0.6), 0 10px 20px rgba(0,0,0,0.4)",
        "depth-hover": "0 35px 70px rgba(0,0,0,0.7), 0 15px 30px rgba(0,0,0,0.5)",
        glass: "inset 0 1px 0 rgba(255,255,255,0.1), 0 20px 40px rgba(0,0,0,0.4)",
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "hero-gradient":
          "linear-gradient(135deg, #061A2F 0%, #0A2E57 40%, #061A2F 100%)",
        "card-gradient":
          "linear-gradient(135deg, rgba(13,39,66,0.9) 0%, rgba(6,26,47,0.85) 100%)",
        "accent-gradient": "linear-gradient(135deg, #0EA5E9, #0369A1)",
        "danger-gradient": "linear-gradient(135deg, #EF4444, #b91c1c)",
      },
      animation: {
        "fade-up": "fadeUp 0.6s ease forwards",
        "fade-in": "fadeIn 0.5s ease forwards",
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "spin-slow": "spin 3s linear infinite",
        float: "float 4s ease-in-out infinite",
        "glow-pulse": "glowPulse 2s ease-in-out infinite",
        scan: "scan 2s linear infinite",
        "count-up": "countUp 1.5s ease forwards",
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: 0, transform: "translateY(30px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        fadeIn: {
          "0%": { opacity: 0 },
          "100%": { opacity: 1 },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-12px)" },
        },
        glowPulse: {
          "0%, 100%": { boxShadow: "0 0 20px rgba(14,165,233,0.3)" },
          "50%": { boxShadow: "0 0 40px rgba(14,165,233,0.7)" },
        },
        scan: {
          "0%": { top: "0%" },
          "100%": { top: "100%" },
        },
      },
      backdropBlur: {
        xs: "2px",
      },
      borderRadius: {
        "3xl": "1.5rem",
      },
    },
  },
  plugins: [],
};
