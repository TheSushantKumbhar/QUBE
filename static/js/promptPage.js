
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('quiz-form');
    const quizResult = document.getElementById('quiz-result');
    const quizQuestions = document.getElementById('quiz-questions');
    const saveQuizBtn = document.getElementById('save-quiz');
    const infoBox = document.getElementById('info-box');
    const formBox = document.getElementById('form-box');
    const backToFormBtn = document.getElementById('back-to-form');
    const normalIcon = document.getElementById('normal-icon');
    const loadingIcon = document.getElementById('loading-icon');
    const generateBtn = document.getElementById('generate-btn');
    const quizTitleDisplay = document.getElementById('quiz-title-display');
    const quizSubjectDisplay = document.getElementById('quiz-subject-display');

    let currentQuizData = null; 

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Show loading state in the button only
        normalIcon.classList.add('hidden');
        loadingIcon.classList.remove('hidden');
        generateBtn.disabled = true;

        const title = document.getElementById('title').value;
        const subject = document.getElementById('subject').value;
        const topic = document.getElementById('topic').value;
        const num_questions = document.getElementById('num_questions').value;
        const difficulty = document.getElementById('difficulty').value;

        try {
            const response = await fetch('/AI/generate-ai-quiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic, num_questions, difficulty }),
            });

            const data = await response.json();

            if (response.ok) {
                currentQuizData = {
                    title: title,
                    subject: subject,
                    questions: data.quiz 
                };
                

                infoBox.classList.add('hidden');
                formBox.classList.add('hidden');
                quizResult.classList.remove('hidden');
                
                // Display quiz metadata
                quizTitleDisplay.textContent = title || 'Untitled Quiz';
                quizSubjectDisplay.textContent = subject ? `Subject: ${subject}` : '';
                
                quizQuestions.innerHTML = '';

                // Render questions
                data.quiz.forEach((q, idx) => {
                    const questionDiv = document.createElement('div');
                    questionDiv.classList.add('p-6', 'bg-gray-50', 'dark:bg-zinc-800/50', 'rounded-lg', 'shadow-sm');

                    const questionHeader = document.createElement('div');
                    questionHeader.classList.add('flex', 'items-start', 'mb-4');
                    
                    const questionNumber = document.createElement('div');
                    questionNumber.classList.add('flex', 'items-center', 'justify-center', 'bg-indigo-100', 'dark:bg-indigo-900/30', 'text-indigo-800', 'dark:text-indigo-300', 'font-bold', 'rounded-full', 'w-8', 'h-8', 'mr-3', 'flex-shrink-0');
                    questionNumber.textContent = idx + 1;
                    
                    const questionText = document.createElement('h4');
                    questionText.classList.add('text-lg', 'font-semibold', 'text-gray-800', 'dark:text-gray-200', 'flex-grow');
                    questionText.textContent = q.question;
                    
                    questionHeader.appendChild(questionNumber);
                    questionHeader.appendChild(questionText);
                    questionDiv.appendChild(questionHeader);

                    const optionsList = document.createElement('ul');
                    optionsList.classList.add('space-y-2', 'ml-11');

                    q.options.forEach((opt, optIdx) => {
                        const li = document.createElement('li');
                        li.classList.add('flex', 'items-center', 'text-gray-700', 'dark:text-gray-300');
                        
                        const isCorrect = q.answer.includes(opt);
                        
                        if (isCorrect) {
                            const correctMark = document.createElement('div');
                            correctMark.classList.add('mr-2', 'text-green-500', 'flex-shrink-0');
                            correctMark.innerHTML = `
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                                </svg>
                            `;
                            li.appendChild(correctMark);
                            li.classList.add('font-medium', 'text-green-700', 'dark:text-green-500');
                        } else {
                            const optionMark = document.createElement('div');
                            optionMark.classList.add('mr-2', 'text-gray-400', 'flex-shrink-0');
                            optionMark.innerHTML = `
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clip-rule="evenodd" />
                                </svg>
                            `;
                            li.appendChild(optionMark);
                        }
                        
                        const optText = document.createElement('span');
                        optText.textContent = opt;
                        li.appendChild(optText);
                        
                        optionsList.appendChild(li);
                    });

                    questionDiv.appendChild(optionsList);
                    quizQuestions.appendChild(questionDiv);
                });
            } else {
                alert('Error generating quiz: ' + data.error);
                infoBox.classList.remove('hidden');
                formBox.classList.remove('hidden');
            }
        } catch (error) {
            alert('Error connecting to server. Please try again later.');
            console.error('Error:', error);
        } finally {
            normalIcon.classList.remove('hidden');
            loadingIcon.classList.add('hidden');
            generateBtn.disabled = false;
        }
    });

    backToFormBtn.addEventListener('click', () => {
        // Show form and info boxes, hide results
        infoBox.classList.remove('hidden');
        formBox.classList.remove('hidden');
        quizResult.classList.add('hidden');
        
        // Clear the questions
        quizQuestions.innerHTML = '';
    });

    saveQuizBtn.addEventListener('click', saveQuiz);

    async function saveQuiz() {
        if (!currentQuizData) return alert('No quiz data to save.');
        
        if (!currentQuizData.title) {
            return alert('Quiz title is required.');
        }
        
        if (!currentQuizData.questions || currentQuizData.questions.length === 0) {
            return alert('Quiz must contain at least one question.');
        }

        // Show loading state for save button
        saveQuizBtn.disabled = true;
        saveQuizBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Saving...
        `;

        try {
            const response = await fetch('/AI/save-ai-quiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(currentQuizData),  
            });

            const result = await response.json();

            if (response.ok) {
                // Show success message
                const successToast = document.createElement('div');
                successToast.classList.add(
                    'fixed', 'bottom-4', 'right-4', 'bg-green-600', 'text-white', 
                    'px-6', 'py-3', 'rounded-lg', 'shadow-lg', 'flex', 'items-center',
                    'animate-fade-in'
                );
                successToast.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    Quiz saved successfully!
                `;
                document.body.appendChild(successToast);
                
                setTimeout(() => {
                    successToast.classList.add('animate-fade-out');
                    setTimeout(() => successToast.remove(), 500);
                }, 3000);
                
                setTimeout(() => {
                    window.location.href = '/quiz/myquizzes';
                }, 1500);
            } else {
                alert('Failed to save quiz: ' + result.error);
            }
        } catch (error) {
            alert('Error connecting to server. Please try again later.');
            console.error('Error:', error);
        } finally {
            // Reset save button
            saveQuizBtn.disabled = false;
            saveQuizBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 inline mr-2" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M7.707 10.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V6h5a2 2 0 012 2v7a2 2 0 01-2 2H4a2 2 0 01-2-2V8a2 2 0 012-2h5v5.586l-1.293-1.293zM9 4a1 1 0 012 0v2H9V4z" />
                </svg>
                Save Quiz
            `;
        }
    }

    // Add some CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(10px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeOut {
            0% { opacity: 1; transform: translateY(0); }
            100% { opacity: 0; transform: translateY(10px); }
        }
        .animate-fade-in {
            animation: fadeIn 0.3s ease-out forwards;
        }
        .animate-fade-out {
            animation: fadeOut 0.3s ease-in forwards;
        }
    `;
    document.head.appendChild(style);
});