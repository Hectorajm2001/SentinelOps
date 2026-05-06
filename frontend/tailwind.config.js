export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0a0e1a",
        accent: "#00ff88",
        critical: "#ff4444",
        warning: "#ff9f1a",
        medium: "#f4d35e",
        info: "#4ea8ff"
      },
      fontFamily: {
        sans: ["Space Grotesk", "ui-sans-serif", "system-ui"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular"]
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: 0, transform: "translateY(12px)" },
          "100%": { opacity: 1, transform: "translateY(0)" }
        }
      },
      animation: {
        fadeUp: "fadeUp 0.6s ease-out both"
      }
    }
  },
  plugins: []
};
