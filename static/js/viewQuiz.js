
document.addEventListener('DOMContentLoaded', function () {
    // Toggle Switches
    const toggleSwitches = document.querySelectorAll('input[type="checkbox"].sr-only');
    toggleSwitches.forEach(toggle => {
        toggle.addEventListener('change', function () {
            const dot = this.parentElement.querySelector('.dot');
            const block = this.parentElement.querySelector('.block');
            
            if (this.checked) {
                dot.classList.add('translate-x-6');
                block.classList.replace('bg-gray-300', 'bg-indigo-600');
            } else {
                dot.classList.remove('translate-x-6');
                block.classList.replace('bg-indigo-600', 'bg-gray-300');
            }
        });

        // Set initial state
        if (toggle.checked) {
            toggle.parentElement.querySelector('.dot').classList.add('translate-x-6');
            toggle.parentElement.querySelector('.block').classList.replace('bg-gray-300', 'bg-indigo-600');
        }
    });

    // Availability Radio Buttons
    const availabilityRadios = document.querySelectorAll('input[name="availability_type"]');
    const timeScheduleDiv = document.getElementById('timeSchedule');

    availabilityRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            timeScheduleDiv.classList.toggle('hidden', this.value === 'always');
        });
    });

    // Share Modal
    const shareQuizBtn = document.getElementById('shareQuizBtn');
    const shareModal = document.getElementById('shareModal');
    const closeShareModal = document.getElementById('closeShareModal');
    const copyLinkBtn = document.getElementById('copyLinkBtn');
    const shareLinkInput = document.getElementById('shareLink');

    if (shareQuizBtn) {
        shareQuizBtn.addEventListener('click', function () {
            shareModal.classList.remove('hidden');
            shareModal.classList.add('flex');
        });
    }

    if (closeShareModal) {
        closeShareModal.addEventListener('click', function () {
            shareModal.classList.remove('flex');
            shareModal.classList.add('hidden');
        });
    }

    if (copyLinkBtn) {
        copyLinkBtn.addEventListener('click', function () {
            navigator.clipboard.writeText(shareLinkInput.value).then(() => {
                const originalText = copyLinkBtn.innerHTML;
                copyLinkBtn.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => {
                    copyLinkBtn.innerHTML = originalText;
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy text: ', err);
            });
        });
    }

    // Delete Modal
    const deleteQuizBtn = document.getElementById('deleteQuizBtn');
    const deleteModal = document.getElementById('deleteModal');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');

    if (deleteQuizBtn) {
        deleteQuizBtn.addEventListener('click', function () {
            deleteModal.classList.remove('hidden');
            deleteModal.classList.add('flex');
        });
    }

    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', function () {
            deleteModal.classList.remove('flex');
            deleteModal.classList.add('hidden');
        });
    }

    // Close modals when clicking outside
    window.addEventListener('click', function (event) {
        if (event.target === shareModal) {
            shareModal.classList.remove('flex');
            shareModal.classList.add('hidden');
        }
        if (event.target === deleteModal) {
            deleteModal.classList.remove('flex');
            deleteModal.classList.add('hidden');
        }
    });

    // Form submission
    const quizSettingsForm = document.getElementById('quizSettingsForm');
    if (quizSettingsForm) {
        quizSettingsForm.addEventListener('submit', function (e) {
            e.preventDefault();

            // Get form data
            const formData = new FormData(this);

            // Add always_available flag based on radio selection
            const availabilityType = document.querySelector('input[name="availability_type"]:checked').value;
            formData.append('always_available', availabilityType === 'always');

            // If scheduled but times not set, show error
            if (availabilityType === 'scheduled') {
                const startTime = document.getElementById('start_time').value;
                const endTime = document.getElementById('end_time').value;

                if (!startTime || !endTime) {
                    alert('Please set both start and end times');
                    return;
                }

                // Additional validation: Ensure end time is after start time
                if (startTime >= endTime) {
                    alert('End time must be after start time');
                    return;
                }
            }

            // Submit the form
            fetch(this.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the availability display
                    const availabilityDisplay = document.getElementById('quizAvailability');
                    if (availabilityType === 'always') {
                        availabilityDisplay.textContent = 'Always available';
                    } else {
                        const startTime = new Date(`1970-01-01T${document.getElementById('start_time').value}`);
                        const endTime = new Date(`1970-01-01T${document.getElementById('end_time').value}`);
                        availabilityDisplay.textContent = `${startTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - ${endTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
                    }

                    // Show success message
                    alert('Quiz settings updated successfully');
                } else {
                    alert('Error updating quiz settings: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while updating quiz settings');
            });
        });
    }
});

// Social Media Sharing Function
// function shareOnPlatform(platform, quizUrl) {
//     const quizTitle = '{{ quiz.title }}';
//     const encodedUrl = encodeURIComponent(quizUrl);
//     const encodedTitle = encodeURIComponent(quizTitle);

//     switch(platform) {
//         case 'facebook':
//             window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`, '_blank');
//             break;
//         case 'twitter':
//             window.open(`https://twitter.com/intent/tweet?text=${encodedTitle}&url=${encodedUrl}`, '_blank');
//             break;
//         case 'whatsapp':
//             window.open(`https://wa.me/?text=${encodedTitle} - ${encodedUrl}`, '_blank');
//             break;
//         case 'email':
//             window.location.href = `mailto:?subject=${encodedTitle}&body=Check out this quiz: ${encodedUrl}`;
//             break;
//     }
// }