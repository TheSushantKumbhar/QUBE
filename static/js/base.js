 // Set state immediately before any rendering
 (function() {
    const sidebarState = localStorage.getItem('sidebarOpen');
    if (sidebarState === 'false') {
        // Apply collapsed state to body and html
        document.body.classList.add('sidebar-collapsed');
        
        // Hide text elements
        const navTexts = document.getElementsByClassName('nav-text');
        for (let i = 0; i < navTexts.length; i++) {
            navTexts[i].style.display = 'none';
        }
        
        // Make sure the logo image is visible but text is hidden in collapsed state
        const logoText = document.querySelector('.logo-text');
        if (logoText) {
            logoText.style.display = 'none';
        }
        
        // Ensure the logo image is always visible
        const logoImage = document.querySelector('.logo-image');
        if (logoImage) {
            logoImage.style.display = 'block';
        }
    }
})();

// Main initialization - keep this minimal for fast loading
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const contentContainer = document.getElementById('content-container');
    const logoBtn = document.getElementById('logo-button');
    const navTexts = document.querySelectorAll('.nav-text');
    const logoImage = document.querySelector('.logo-image');
    const logoText = document.querySelector('.logo-text');
    const profileElement = document.getElementById('profile-element');
    
    // Use localStorage to remember sidebar state
    let sidebarOpen = localStorage.getItem('sidebarOpen') !== 'false';
    
    // Set content container height
    contentContainer.style.height = 'calc(100vh - 24px)';

    // Handle profile click in collapsed state
    profileElement.addEventListener('click', function(e) {
        if (document.body.classList.contains('sidebar-collapsed')) {
            // If sidebar is collapsed, navigate directly to profile page
            window.location.href = '/auth/profile';
            // Prevent any default behavior or bubble
            e.preventDefault();
            e.stopPropagation();
        }
    });

    // Function to toggle sidebar with optimized performance
    function toggleSidebar() {
        sidebarOpen = !sidebarOpen;
        localStorage.setItem('sidebarOpen', sidebarOpen);
        
        if (sidebarOpen) {
            // Expand sidebar
            document.documentElement.style.setProperty('--sidebar-width', '13rem');
            document.documentElement.style.setProperty('--content-margin', '13rem');
            document.documentElement.classList.remove('sidebar-collapsed');
            document.body.classList.remove('sidebar-collapsed');
            sidebar.classList.remove('sidebar-collapsed');
            
            // Show logo image and text
            logoImage.style.display = 'block';
            logoText.style.display = 'block';
            
            // Slight delay to show text after width change starts
            setTimeout(() => {
                navTexts.forEach(text => {
                    text.style.display = 'inline';
                });
            }, 50);
        } else {
            // Hide text first for smoother transition
            navTexts.forEach(text => {
                text.style.display = 'none';
            });
            
            // Ensure logo image stays visible but hide text
            logoImage.style.display = 'block';
            logoText.style.display = 'none';
            
            // Immediately start width transition
            document.documentElement.style.setProperty('--sidebar-width', '6rem');
            document.documentElement.style.setProperty('--content-margin', '6rem');
            document.documentElement.classList.add('sidebar-collapsed');
            document.body.classList.add('sidebar-collapsed');
            sidebar.classList.add('sidebar-collapsed');
        }
    }

    // Add event listener to logo button
    logoBtn.addEventListener('click', toggleSidebar);
    
    // Preload images for faster rendering
    function preloadImages() {
        const images = document.querySelectorAll('img');
        for (let img of images) {
            const src = img.getAttribute('src');
            if (src) {
                const newImg = new Image();
                newImg.src = src;
            }
        }
    }
    
    // Preload images
    preloadImages();
    
    // Show page once everything is initialized (faster fade-in)
    requestAnimationFrame(() => {
        document.body.classList.add('loaded');
    });
});