/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        void: '#140d0a',
        surface: '#1c1410',
        raised: '#2a201a',
        subtle: '#3a2e26',
        primary: '#f0e4d8',
        secondary: '#b89f88',
        muted: '#8a7560',
        glow: '#c87040',
        'glow-hover': '#e08a5a',
        'glow-faint': 'rgba(200, 112, 64, 0.08)',
        'glow-10': 'rgba(200, 112, 64, 0.10)',
        'glow-20': 'rgba(200, 112, 64, 0.20)',
        plan: '#9b6b8a',
        build: '#d4a04a',
        test: '#7a9b5e',
        review: '#6b8a9b',
        document: '#b89bb0',
        deploy: '#b35a30',
        monitor: '#5a9ba0',
        pass: '#8ab06a',
        fail: '#c25450',
        warning: '#c4a05a',
      },
      fontFamily: {
        sans: ['IBM Plex Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
};
