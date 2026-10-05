/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#eef7f5',
        sidebar: {
          DEFAULT: '#0f3838',
          hover: '#174d4d',
          active: '#1f5c5c',
          text: '#e6f5f3',
          muted: '#8cb0ad',
        },
        primary: {
          DEFAULT: '#d99b00',
          hover: '#b88400',
          light: '#fef3c7',
        },
        surface: {
          DEFAULT: '#ffffff',
          secondary: '#f4faf8',
          mint: '#e4f2ef',
        },
        input: '#e4f2ef',
        text: {
          primary: '#112a2a',
          secondary: '#4a6865',
          light: '#789c97',
        },
        border: {
          DEFAULT: '#cce5e0',
          dark: '#a8d1c9',
        },
        accent: {
          success: '#0d9488',
          warning: '#d97706',
          error: '#e11d48',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
