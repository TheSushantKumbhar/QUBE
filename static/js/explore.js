 function updateCurrentTime() {
        const now = new Date();
        let hours = now.getHours();
        const minutes = now.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        
        hours = hours % 12;
        hours = hours ? hours : 12; // hour '0' should be '12'
        const paddedMinutes = minutes < 10 ? '0' + minutes : minutes;
        
        const timeString = `${hours}:${paddedMinutes} ${ampm}`;
        document.getElementById('current-time').textContent = timeString;
    }

    // Call it once immediately
    updateCurrentTime();

    // Optionally update it every minute
    setInterval(updateCurrentTime, 60000);