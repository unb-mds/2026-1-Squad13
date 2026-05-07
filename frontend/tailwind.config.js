/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['DM Sans', 'sans-serif'],
        display: ['Syne', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        ink: {
          50: '#f0f0f5',
          100: '#d9d9e8',
          200: '#b3b3d1',
          300: '#8080b0',
          400: '#5a5a91',
          500: '#3d3d6b',
          600: '#2e2e52',
          700: '#1e1e38',
          800: '#12121f',
          900: '#080810',
        },
        volt: {
          50: '#f5ffe0',
          100: '#e8ffa8',
          200: '#d4ff6e',
          300: '#c2ff3d',
          400: '#b2ff00',
          500: '#9de800',
          600: '#7abd00',
          700: '#5a8f00',
          800: '#3d6200',
          900: '#1e3100',
        },
        amber: {
          400: '#fbbf24',
          500: '#f59e0b',
        },
        rose: {
          400: '#fb7185',
          500: '#f43f5e',
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'slide-in': 'slideIn 0.3s ease-out',
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: '0' }, to: { opacity: '1' } },
        slideUp: { from: { opacity: '0', transform: 'translateY(16px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        slideIn: { from: { opacity: '0', transform: 'translateX(-16px)' }, to: { opacity: '1', transform: 'translateX(0)' } },
      },
    },
  },
  plugins: [],
}
