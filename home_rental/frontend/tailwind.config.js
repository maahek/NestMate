/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  safelist: [
    'bg-navy', 'bg-navy-mid', 'bg-navy-light',
    'bg-ochre', 'bg-ochre-light', 'bg-ochre-bg',
    'bg-cream',
    'text-navy', 'text-navy-mid', 'text-navy-light',
    'text-ochre', 'text-ochre-light', 'text-ochre-bg',
    'text-cream',
    'border-navy', 'border-ochre', 'border-ochre-light',
    'from-navy', 'to-navy', 'from-ochre', 'to-ochre',
    'ring-ochre', 'ring-navy',
    'hover:bg-navy', 'hover:bg-ochre', 'hover:text-ochre',
    'focus:border-ochre', 'focus:ring-ochre',
    'gradient-text', 'glass',
    'btn-primary', 'btn-ghost', 'btn-ochre',
    'form-input', 'card',
    'animate-fade-in-up', 'animate-slide-in',
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#0f172a',
          mid:     '#1e293b',
          light:   '#334155',
        },
        ochre: {
          DEFAULT: '#d97706',
          light:   '#fbbf24',
          bg:      '#fef3c7',
        },
        cream: '#fffbf5',
      },
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        body:    ['DM Sans', 'sans-serif'],
      },
      boxShadow: {
        card: '0 4px 24px rgba(15,23,42,0.08)',
        lg:   '0 12px 48px rgba(15,23,42,0.14)',
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.5s ease forwards',
        'slide-in':   'slideIn 0.3s ease',
      },
      keyframes: {
        fadeInUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          from: { opacity: '0', transform: 'translateX(20px)' },
          to:   { opacity: '1', transform: 'translateX(0)' },
        },
      },
    },
  },
  plugins: [],
}