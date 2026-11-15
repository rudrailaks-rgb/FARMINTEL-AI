/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#070B13',
        surface: '#0E1526',
        card: '#141D33',
        border: '#1F2B48',
        accent: {
          emerald: '#10B981',
          cyan: '#06B6D4',
          amber: '#F59E0B',
          rose: '#F43F5E',
          blue: '#3B82F6'
        }
      }
    },
  },
  plugins: [],
}
