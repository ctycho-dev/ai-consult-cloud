/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      outlineColor: {
        primary_green: '#2e7d32',
      },
      colors: {
        'sidebar-background': 'hsl(0, 0%, 98%)',
        'sidebar-foreground': 'hsl(240, 5.3%, 26.1%)',
        'sidebar-accent': 'hsl(240, 4.8%, 95.9%)',
        'sidebar-accent-foreground': 'hsl(240, 5.9%, 10%)',
        'sidebar-border': 'hsl(220, 13%, 91%)',
        'sidebar-ring': 'hsl(217.2, 91.2%, 59.8%)',
        
        'background': 'hsl(0, 0%, 100%)',
        'foreground': 'hsl(240, 10%, 3.9%)',
        'card': 'hsl(0, 0%, 100%)',
        'card-foreground': 'hsl(240, 10%, 3.9%)',
        'popover': 'hsl(0, 0%, 100%)',
        'popover-foreground': 'hsl(240, 10%, 3.9%)',
        'primary': 'hsl(240, 5.9%, 10%)',
        'primary-foreground': 'hsl(0, 0%, 98%)',
        'secondary': 'hsl(240, 4.8%, 95.9%)',
        'secondary-foreground': 'hsl(240, 5.9%, 10%)',
        'muted': 'hsl(240, 4.8%, 95.9%)',
        'muted-foreground': 'hsl(240, 3.8%, 46.1%)',
        'accent': 'hsl(240, 4.8%, 95.9%)',
        'accent-foreground': 'hsl(240, 5.9%, 10%)',
        'destructive': 'hsl(0, 84.2%, 60.2%)',
        'destructive-foreground': 'hsl(0, 0%, 98%)',
        'border': 'hsl(240, 5.9%, 90%)',
        'input': 'hsl(240, 5.9%, 90%)',
        'ring': 'hsl(240, 5.9%, 10%)',
      },
      borderRadius: {
        'radius': '0.5rem',
      }
    },
  },
  plugins: [],
}