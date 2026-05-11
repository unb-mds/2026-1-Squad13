/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        surface: {
          0: '#0a0a0f',
          1: '#111118',
          2: '#18181f',
          3: '#1f1f28',
          4: '#26262f',
        },
        border: {
          subtle: '#2a2a35',
          default: '#3a3a48',
        },
        accent: {
          blue: '#3b82f6',
          purple: '#8b5cf6',
          green: '#10b981',
          yellow: '#f59e0b',
          red: '#ef4444',
          cyan: '#06b6d4',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        glow: '0 0 20px rgba(59,130,246,0.15)',
        'glow-purple': '0 0 20px rgba(139,92,246,0.15)',
        'glow-green': '0 0 20px rgba(16,185,129,0.15)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        pulse: 'pulse 2s cubic-bezier(0.4,0,0.6,1) infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: '0' }, to: { opacity: '1' } },
        slideUp: { from: { opacity: '0', transform: 'translateY(8px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
}
