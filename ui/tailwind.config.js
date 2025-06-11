/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,vue}",
  ],
  theme: {
    extend: {
      animation: {
        'color-pulse': 'color-pulse 2s ease-in-out infinite'
      }
    },
  },
  plugins: [],
}
