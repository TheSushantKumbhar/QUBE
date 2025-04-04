// Add this code to your main JavaScript file or include it in a script tag

// Function to create and insert the loading overlay with your GIF
function createLoadingOverlay() {
    // Create the overlay element
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.right = '0';
    overlay.style.bottom = '0';
    overlay.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
    overlay.style.display = 'flex';
    overlay.style.justifyContent = 'center';
    overlay.style.alignItems = 'center';
    overlay.style.zIndex = '9999';
    overlay.style.transition = 'opacity 0.3s ease-in-out';
    overlay.style.opacity = '0';
    overlay.style.pointerEvents = 'none';
  
    // Create the container for the GIF
    const container = document.createElement('div');
    container.style.backgroundColor = 'white';
    container.style.padding = '1.5rem';
    container.style.borderRadius = '0.5rem';
    container.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1)';
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.alignItems = 'center';
  
    // Add your GIF
    const gif = document.createElement('img');
    gif.src = '/static/images/loading.gif'; // Replace with the actual path to your GIF
    gif.alt = 'Loading...';
    gif.style.width = '64px'; // Adjust size as needed
    gif.style.height = 'auto';
  
    // Optional: Add loading text below the GIF
    const text = document.createElement('p');
    text.textContent = 'Loading...';
    text.style.marginTop = '0.75rem';
    text.style.color = '#4f46e5'; // indigo-600
    text.style.fontWeight = '500';
  
    // Assemble the elements
    container.appendChild(gif);
    container.appendChild(text);
    overlay.appendChild(container);
    
    // Add to document
    document.body.appendChild(overlay);
    
    return overlay;
  }
  
  // Get or create the loading overlay
  function getLoadingOverlay() {
    let overlay = document.getElementById('loading-overlay');
    if (!overlay) {
      overlay = createLoadingOverlay();
    }
    return overlay;
  }
  
  // Show the loading indicator
  function showLoading() {
    const overlay = getLoadingOverlay();
    overlay.style.opacity = '1';
    overlay.style.pointerEvents = 'auto';
  }
  
  // Hide the loading indicator
  function hideLoading() {
    const overlay = getLoadingOverlay();
    overlay.style.opacity = '0';
    overlay.style.pointerEvents = 'none';
  }
  
  // Example usage for page transitions:
  
  // 1. Add event listeners to all internal links
  document.addEventListener('DOMContentLoaded', function() {
    // For links that navigate within your site
    const internalLinks = document.querySelectorAll('a:not([target="_blank"])');
    internalLinks.forEach(link => {
      // Only apply to links within your domain
      if (link.hostname === window.location.hostname) {
        link.addEventListener('click', function(e) {
          // Don't show loading for hash links (in-page navigation)
          if (this.getAttribute('href').startsWith('#')) return;
          
          showLoading();
        });
      }
    });
    
    // Hide loading when page is fully loaded
    window.addEventListener('load', hideLoading);
  });
  
  // 2. For form submissions
  document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
      form.addEventListener('submit', function() {
        showLoading();
      });
    });
  });
  
  // 3. For AJAX navigation (if you're using it)
  // This is a simplified example - adjust based on your actual AJAX implementation
  function navigateWithAjax(url) {
    showLoading();
    
    fetch(url)
      .then(response => response.text())
      .then(html => {
        // Update page content
        document.getElementById('content-container').innerHTML = html;
        hideLoading();
        history.pushState({}, '', url);
      })
      .catch(error => {
        console.error('Navigation error:', error);
        hideLoading();
      });
  }