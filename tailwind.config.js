/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        void: '#09090B',
        surface: '#111113',
        raised: '#1A1A1F',
        subtle: '#232329',
        primary: '#F4F4F5',
        secondary: '#A1A1AA',
        muted: '#71717A',
        glow: '#6366F1',
        'glow-hover': '#818CF8',
        'glow-faint': 'rgba(99, 102, 241, 0.08)',
        'glow-10': 'rgba(99, 102, 241, 0.10)',
        'glow-20': 'rgba(99, 102, 241, 0.20)',
        plan: '#8B5CF6',
        build: '#F59E0B',
        test: '#10B981',
        review: '#3B82F6',
        document: '#A78BFA',
        deploy: '#F97316',
        monitor: '#06B6D4',
        pass: '#22C55E',
        fail: '#EF4444',
        warning: '#EAB308',
      },
      fontFamily: {
        sans: ['IBM Plex Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
};
