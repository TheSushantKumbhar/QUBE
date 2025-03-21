function clearLocalStorageBeforeLogout() {
    localStorage.removeItem('previewQuizData'); // Remove specific quiz data
    localStorage.clear(); // (Optional) Clears all localStorage data
}
function previewImage(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById('profile-preview').src = e.target.result;
            document.getElementById('upload-box-text').classList.add('hidden');
            document.getElementById('image-updated-notice').classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }
}
