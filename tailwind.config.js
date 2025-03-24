// /** @type {import('tailwindcss').Config} */
// module.exports = {
//   content: ["./templates/**/*.html", "./static/css/**/*.css"],
//   theme: {
//     extend: {},
//   },
//   plugins: [],
// }

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./static/css/**/*.css"],
  darkMode: 'class', // Enables dark mode using the 'class' strategy
  theme: {
    extend: {
      keyframes: {
        pulse: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.7 },
        }
      },
      animation: {
        pulse: 'pulse 1s infinite',
      }
    }
  },
  plugins: [],
};
