import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#14222f",
        "sky-soft": "#e6f4fb",
        "sand-soft": "#f7f5ef",
        teal: "#0d7c8a",
        slate: "#415568",
      },
      boxShadow: {
        card: "0 12px 30px rgba(20, 34, 47, 0.12)",
      },
    },
  },
  plugins: [],
};

export default config;

