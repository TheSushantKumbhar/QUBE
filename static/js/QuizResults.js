 // Theme toggling
 const themeToggle = document.getElementById('theme-toggle');
        
 if (localStorage.getItem('theme') === 'dark' || 
     (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
     document.documentElement.classList.add('dark');
 } else {
     document.documentElement.classList.remove('dark');
 }
 
 themeToggle.addEventListener('click', function() {
     if (document.documentElement.classList.contains('dark')) {
         document.documentElement.classList.remove('dark');
         localStorage.setItem('theme', 'light');
     } else {
         document.documentElement.classList.add('dark');
         localStorage.setItem('theme', 'dark');
     }
     updateChart(); // Redraw chart with new theme colors
 });
 
 // Accordion functionality
 document.querySelectorAll('.accordion-header').forEach(header => {
     header.addEventListener('click', () => {
         const content = header.nextElementSibling;
         const icon = header.querySelector('.fa-chevron-down');
         
         content.classList.toggle('hidden');
         icon.classList.toggle('rotate-180');
     });
 });
 
 // Chart.js setup
 function updateChart() {
     const isDark = document.documentElement.classList.contains('dark');
     const textColor = isDark ? '#D1D5DB' : '#374151';
     const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
     
     // Count correct and incorrect answers
    //  const correctCount = {{ questions|selectattr('is_correct', 'eq', true)|list|length }};
    //  const incorrectCount = {{ questions|selectattr('is_correct', 'eq', false)|list|length }};
    const questions = JSON.parse('{{ questions | tojson | safe }}');
    const correctCount = questions.filter(q => q.is_correct === true).length;
    const incorrectCount = questions.filter(q => q.is_correct === false).length;
     
     const ctx = document.getElementById('resultsChart').getContext('2d');
     
     // Clear previous chart if it exists
     if (window.resultsChart) {
         window.resultsChart.destroy();
     }
     
     window.resultsChart = new Chart(ctx, {
         type: 'pie',
         data: {
             labels: ['Correct', 'Incorrect'],
             datasets: [{
                 data: [correctCount, incorrectCount],
                 backgroundColor: [
                     '#10B981', // green-500
                     '#EF4444'  // red-500
                 ],
                 borderWidth: 0
             }]
         },
         options: {
             responsive: true,
             maintainAspectRatio: false,
             plugins: {
                 legend: {
                     position: 'right',
                     labels: {
                         color: textColor,
                         font: {
                             size: 14
                         },
                         padding: 20
                     }
                 },
                 tooltip: {
                     callbacks: {
                         label: function(context) {
                             const label = context.label || '';
                             const value = context.raw || 0;
                             const total = context.dataset.data.reduce((a, b) => a + b, 0);
                             const percentage = Math.round((value / total) * 100);
                             return `${label}: ${value} (${percentage}%)`;
                         }
                     }
                 }
             }
         }
     });
 }
 
 // Initialize chart on page load
 document.addEventListener('DOMContentLoaded', updateChart);