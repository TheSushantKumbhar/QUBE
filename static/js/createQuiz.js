let currentPage = 1;
let questionCount = 1;

function showPage(page) {
    document.querySelectorAll('.question-page').forEach(el => el.classList.remove('active'));
    document.getElementById('page' + page).classList.add('active');
    currentPage = page;
}

function addQuestion() {
    questionCount++;
    const newQuestion = `
        <div class="question-page active" id="page${questionCount + 2}">
            <h2 class="text-2xl font-semibold mb-4">Question <span>${questionCount}</span></h2>
            <div class="image-upload" onclick="document.getElementById('questionImage${questionCount}').click()">
                <p>Click to add an image</p>
                <img id="previewImage${questionCount}">
                <input type="file" id="questionImage${questionCount}" accept="image/*" onchange="previewFile(event, ${questionCount})">
            </div>
            <input type="text" class="w-full p-2 border rounded mt-2" placeholder="Enter question" required>
            <div class="grid grid-cols-2 gap-2 mt-4">
                <input type="text" class="option p-2 border rounded" placeholder="Option 1" required>
                <input type="text" class="option p-2 border rounded" placeholder="Option 2" required>
                <input type="text" class="option p-2 border rounded" placeholder="Option 3" required>
                <input type="text" class="option p-2 border rounded" placeholder="Option 4" required>
            </div>

            <div class="flex justify-between mt-6">
                <button type="button" onclick="showPage(${questionCount + 1})" class="bg-gray-500 text-white px-4 py-2 rounded">Back</button>
                <button type="button" onclick="addQuestion()" class="bg-green-500 text-white px-6 py-3 rounded-lg shadow-md hover:bg-green-600 transition duration-300">
                    Add Question
                </button>
            </div>
        </div>`;
    
    document.getElementById('questionsContainer').insertAdjacentHTML('beforeend', newQuestion);
    document.getElementById('page' + (questionCount + 2)).scrollIntoView({ behavior: 'smooth' });
}

function previewFile(event, index) {
    const file = event.target.files[0];
    const preview = document.getElementById('previewImage' + index);
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = "block";
        };
        reader.readAsDataURL(file);
    }
}