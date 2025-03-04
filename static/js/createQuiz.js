function addQuestion() {
    let container = document.getElementById('questionsContainer');
    let questionDiv = document.createElement('div');
    questionDiv.classList.add('question', 'p-4', 'border', 'rounded', 'bg-gray-50');
    questionDiv.innerHTML = `
        <input type="text" class="question_text w-full p-2 border rounded" placeholder="Enter question" required>
        <div class="grid grid-cols-2 gap-2 mt-2">
            <input type="text" class="option p-2 border rounded" placeholder="Option 1" required>
            <input type="text" class="option p-2 border rounded" placeholder="Option 2" required>
            <input type="text" class="option p-2 border rounded" placeholder="Option 3" required>
            <input type="text" class="option p-2 border rounded" placeholder="Option 4" required>
        </div>
        <input type="text" class="correct_answer w-full p-2 border rounded mt-2" placeholder="Correct Answer" required>
    `;
    container.appendChild(questionDiv);
}

document.getElementById('quizForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let questions = [];
    document.querySelectorAll('.question').forEach(q => {
        let options = Array.from(q.getElementsByClassName('option')).map(input => input.value);
        questions.push({
            question_text: q.querySelector('.question_text').value,
            options: options,
            correct_answer: q.querySelector('.correct_answer').value
        });
    });

    let quizData = {
        title: document.getElementById('quizTitle').value,
        description: document.getElementById('quizDescription').value,
        questions: questions
    };

    fetch('/create_quiz', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(quizData)
    }).then(response => response.json())
      .then(data => alert(data.message));
});
