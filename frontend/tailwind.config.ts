import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./features/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],

  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-geist-sans)", "sans-serif"],
      },

      colors: {
        primary: "var(--primary)",
        secondary: "var(--secondary)",
        tertiary: "var(--tertiary)",

        background: {
          DEFAULT: "var(--bg-base)",
          surface: "var(--bg-surface)",
          card: "var(--bg-card)",
          elevated: "var(--bg-elevated)",
          hover: "var(--bg-hover)",
        },

        border: {
          DEFAULT: "var(--border)",
          subtle: "var(--border-subtle)",
        },

        text: {
          primary: "var(--text-primary)",
          secondary: "var(--text-secondary)",
          muted: "var(--text-muted)",
        },

        success: "var(--success)",
        warning: "var(--warning)",
        danger: "var(--danger)",

        chart: {
          red: "var(--chart-red)",
          teal: "var(--chart-teal)",
          green: "var(--chart-green)",
          yellow: "var(--chart-yellow)",
          gray: "var(--chart-gray)",
        },
      },

      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
      },

      boxShadow: {
        sm: "var(--shadow-sm)",
        md: "var(--shadow-md)",
      },

      transitionDuration: {
        fast: "150ms",
        normal: "250ms",
      },

      maxWidth: {
        app: "1600px",
      },
    },
  },

  plugins: [],
};

export default config;