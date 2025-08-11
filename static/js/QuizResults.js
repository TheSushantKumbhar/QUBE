 // Accordion functionality
 document.querySelectorAll('.accordion-header').forEach(header => {
     header.addEventListener('click', () => {
         const content = header.nextElementSibling;
         const icon = header.querySelector('.fa-chevron-down');
         
         content.classList.toggle('hidden');
         icon.classList.toggle('rotate-180');
     });
 });
 
