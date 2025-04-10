// darkmode.js
document.addEventListener('DOMContentLoaded', () => {
    // Check if user has a saved preference
    function initTheme() {
      if (localStorage.theme === 'dark' || 
          (!('theme' in localStorage) && 
          window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
    
    // Initialize the theme
    initTheme();
    
    // Add event listener to toggle button
    const darkToggle = document.getElementById('dark-toggle');
    if (darkToggle) {
      darkToggle.addEventListener('click', () => {
        // Toggle dark mode
        if (document.documentElement.classList.contains('dark')) {
          document.documentElement.classList.remove('dark');
          localStorage.theme = 'light'; 
        } else {
          document.documentElement.classList.add('dark');
          localStorage.theme = 'dark';
        }
      });
    }
  });