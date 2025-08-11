 // Set state immediately before any rendering
 (function() {
    const sidebarState = localStorage.getItem('sidebarOpen');
    if (sidebarState === 'false') {
        document.body.classList.add('sidebar-collapsed');
        
        const navTexts = document.getElementsByClassName('nav-text');
        for (let i = 0; i < navTexts.length; i++) {
            navTexts[i].style.display = 'none';
        }
        
        const logoText = document.querySelector('.logo-text');
        if (logoText) {
            logoText.style.display = 'none';
        }

        const logoImage = document.querySelector('.logo-image');
        if (logoImage) {
            logoImage.style.display = 'block';
        }
    }
})();

document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const contentContainer = document.getElementById('content-container');
    const logoBtn = document.getElementById('logo-button');
    const navTexts = document.querySelectorAll('.nav-text');
    const logoImage = document.querySelector('.logo-image');
    const logoText = document.querySelector('.logo-text');
    const profileElement = document.getElementById('profile-element');
    
    let sidebarOpen = localStorage.getItem('sidebarOpen') !== 'false';
    
    // Set content container height
    contentContainer.style.height = 'calc(100vh - 24px)';

    // Handle profile click in collapsed state
    profileElement.addEventListener('click', function(e) {
        if (document.body.classList.contains('sidebar-collapsed')) {
            window.location.href = '/auth/update_profile';
            e.preventDefault();
            e.stopPropagation();
        }
    });

    function toggleSidebar() {
        sidebarOpen = !sidebarOpen;
        localStorage.setItem('sidebarOpen', sidebarOpen);
        
        if (sidebarOpen) {
          
            document.documentElement.style.setProperty('--sidebar-width', '13rem');
            document.documentElement.style.setProperty('--content-margin', '13rem');
            document.documentElement.classList.remove('sidebar-collapsed');
            document.body.classList.remove('sidebar-collapsed');
            sidebar.classList.remove('sidebar-collapsed');
            
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
            
            logoImage.style.display = 'block';
            logoText.style.display = 'none';
            
            document.documentElement.style.setProperty('--sidebar-width', '6rem');
            document.documentElement.style.setProperty('--content-margin', '6rem');
            document.documentElement.classList.add('sidebar-collapsed');
            document.body.classList.add('sidebar-collapsed');
            sidebar.classList.add('sidebar-collapsed');
        }
    }

    logoBtn.addEventListener('click', toggleSidebar);
    
    // Show page once everything is initialized (faster fade-in)
    requestAnimationFrame(() => {
        document.body.classList.add('loaded');
    });
});