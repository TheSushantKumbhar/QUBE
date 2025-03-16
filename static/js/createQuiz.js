let currentQuestionIndex = 0;

function updateQuestionView() {
    const questions = document.querySelectorAll(".question");
    const container = document.getElementById("questionsContainer");

    if (currentQuestionIndex < 0) currentQuestionIndex = 0;
    if (currentQuestionIndex >= questions.length) currentQuestionIndex = questions.length - 1;

    const offset = -currentQuestionIndex * 100;
    container.style.transform = `translateX(${offset}%)`;
}

function nextQuestion() {
    const totalQuestions = document.querySelectorAll(".question").length;
    if (currentQuestionIndex < totalQuestions - 1) {
        currentQuestionIndex++;
        updateQuestionView();
    }
}

function prevQuestion() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        updateQuestionView();
    }
}

function addQuestion() {
    const container = document.getElementById("questionsContainer");

    const questionDiv = document.createElement("div");
    questionDiv.classList.add("question", "p-4", "border", "rounded", "bg-gray-50", "w-full");
    questionDiv.innerHTML = `
        <input type="file" class="question_image w-full p-2 border rounded mb-2">
        <input type="text" class="question_text w-full p-2 border rounded" placeholder="Enter question" required>
        <div class="grid grid-cols-2 gap-2 mt-2">
            <div class="flex items-center space-x-2">
                <input type="file" class="option_image p-2 border rounded">
                <input type="text" class="option p-2 border rounded" placeholder="Option 1" required>
            </div>
            <div class="flex items-center space-x-2">
                <input type="file" class="option_image p-2 border rounded">
                <input type="text" class="option p-2 border rounded" placeholder="Option 2" required>
            </div>
            <div class="flex items-center space-x-2">
                <input type="file" class="option_image p-2 border rounded">
                <input type="text" class="option p-2 border rounded" placeholder="Option 3" required>
            </div>
            <div class="flex items-center space-x-2">
                <input type="file" class="option_image p-2 border rounded">
                <input type="text" class="option p-2 border rounded" placeholder="Option 4" required>
            </div>
        </div>
        <input type="text" class="correct_answer w-full p-2 border rounded mt-2" placeholder="Correct Answer" required>
    `;

    container.appendChild(questionDiv);
    currentQuestionIndex = document.querySelectorAll(".question").length - 1;
    updateQuestionView();
}
