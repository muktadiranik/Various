// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        discord: {
          primary: '#36393f',
          secondary: '#2f3136',
          tertiary: '#202225',
          accent: '#5865f2',
          'accent-hover': '#4752c4',
          danger: '#ed4245',
          success: '#3ba55d',
          warning: '#faa81a',
          text: '#ffffff',
          'text-muted': '#b9bbbe',
        },
      },
      animation: {
        'spin-slow': 'spin 2s linear infinite',
        'ping-slow': 'ping 3s cubic-bezier(0, 0, 0.2, 1) infinite',
      },
    },
  },
  plugins: [],
}