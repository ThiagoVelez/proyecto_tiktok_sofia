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
        dark: {
          950: '#07080d',
          900: '#0c0d14',
          850: '#11121d',
          800: '#171926',
          700: '#23263b',
          600: '#323652',
        },
        brand: {
          pink: '#ff2d8d',
          purple: '#8a2be2',
          gradientStart: '#9333ea',
          gradientEnd: '#ec4899',
          cyan: '#00f2fe',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      screens: {
        'xs': '420px',
      },
      boxShadow: {
        'neon': '0 0 20px rgba(236, 72, 153, 0.35)',
        'cyan-glow': '0 0 15px rgba(0, 242, 254, 0.3)',
      }
    },
  },
  plugins: [],
}
