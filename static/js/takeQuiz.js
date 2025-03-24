
document.addEventListener('DOMContentLoaded', function() {
    // Theme toggling
    const themeToggle = document.getElementById('theme-toggle');
    
    // Check for saved theme preference or respect OS preference
    if (localStorage.getItem('theme') === 'dark' || 
        (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
    
    // Toggle theme
    themeToggle.addEventListener('click', function() {
        if (document.documentElement.classList.contains('dark')) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        }
    });

    // Initialize variables
    const questions = document.querySelectorAll('.question-container');
    const totalQuestions = questions.length;
    let currentQuestionIndex = 0;
    const answeredQuestions = new Set();
    const flaggedQuestions = new Set();
    
    // Timer variables
    let timerSeconds = 0;
    let timerInterval;
    const startTime = new Date();
    const timerDisplay = document.getElementById('timer-display');
    const quizTimer = document.getElementById('quiz-timer');
    
    // Modal setup
    const submitModal = document.getElementById('submitConfirmModal');
    const cancelSubmit = document.getElementById('cancel-submit');
    
    // Start the timer
    startTimer();
    
    // Initialize question navigation
    initializeQuestionNavigation();
    
    // Handle option selection to mark questions as answered
    document.querySelectorAll('input[type="radio"], input[type="checkbox"]').forEach(input => {
        input.addEventListener('change', function() {
            const questionId = this.name.split('-')[1];
            const questionContainer = document.getElementById('question-' + questionId);
            const questionIndex = Array.from(questions).indexOf(questionContainer);
            
            // For radio buttons, a selection means the question is answered
            if (this.type === 'radio') {
                answeredQuestions.add(questionIndex);
            } 
            // For checkboxes, we need to check if any checkbox in the group is checked
            else {
                const checkboxes = document.querySelectorAll(`input[name="${this.name}"]:checked`);
                if (checkboxes.length > 0) {
                    answeredQuestions.add(questionIndex);
                } else {
                    answeredQuestions.delete(questionIndex);
                }
            }
            
            updateQuestionStatus();
        });
    });
    
    // Flag buttons
    document.querySelectorAll('.flag-btn').forEach((button, index) => {
        button.addEventListener('click', function() {
            this.classList.toggle('text-red-500');
            this.classList.toggle('dark:text-red-400');
            if (this.classList.contains('text-red-500')) {
                flaggedQuestions.add(index);
            } else {
                flaggedQuestions.delete(index);
            }
            updateQuestionStatus();
        });
    });
    
    // Review flagged questions button
    document.getElementById('review-flagged').addEventListener('click', () => {
        if (flaggedQuestions.size === 0) {
            alert('No questions have been flagged for review.');
            return;
        }
        
        // Go to the first flagged question
        const firstFlagged = Math.min(...Array.from(flaggedQuestions));
        goToQuestion(firstFlagged);
    });
    
    // Navigation buttons
    document.querySelectorAll('.next-question').forEach((button, index) => {
        button.addEventListener('click', () => {
            if (index === totalQuestions - 1) {
                // This is the last question's "Submit" button
                document.getElementById('submit-quiz').click();
            } else if (currentQuestionIndex < totalQuestions - 1) {
                goToQuestion(currentQuestionIndex + 1);
            }
        });
    });
    
    document.querySelectorAll('.prev-question').forEach((button) => {
        button.addEventListener('click', () => {
            if (currentQuestionIndex > 0) {
                goToQuestion(currentQuestionIndex - 1);
            }
        });
    });
    
    // Submit quiz button
    document.getElementById('submit-quiz').addEventListener('click', () => {
        const unansweredCount = totalQuestions - answeredQuestions.size;
        const unansweredWarning = document.getElementById('unanswered-warning');
        const unansweredCountEl = document.getElementById('unanswered-count');
        
        if (unansweredCount > 0) {
            unansweredWarning.classList.remove('hidden');
            unansweredCountEl.textContent = unansweredCount;
        } else {
            unansweredWarning.classList.add('hidden');
        }
        
        submitModal.classList.remove('hidden');
    });
    
    // Cancel submit button in modal
    cancelSubmit.addEventListener('click', () => {
        submitModal.classList.add('hidden');
    });
    
    // Confirm submit button in modal
    document.getElementById('confirm-submit').addEventListener('click', () => {
        submitQuiz();
        submitModal.classList.add('hidden');
    });
    
    // Function to go to a specific question
    function goToQuestion(index) {
        // Hide current question and show new one
        questions[currentQuestionIndex].classList.add('hidden');
        questions[currentQuestionIndex].classList.remove('block');
        currentQuestionIndex = index;
        questions[currentQuestionIndex].classList.remove('hidden');
        questions[currentQuestionIndex].classList.add('block');
        updateProgress();
        
        // Update current question indicator in the sidebar
        document.querySelectorAll('.question-number-btn').forEach((btn, idx) => {
            if (idx === currentQuestionIndex) {
                btn.classList.add('ring-2', 'ring-blue-500', 'dark:ring-blue-400');
            } else {
                btn.classList.remove('ring-2', 'ring-blue-500', 'dark:ring-blue-400');
            }
        });
        
        // Adjust previous button for first question
        const prevButtons = document.querySelectorAll('.prev-question');
        prevButtons.forEach(btn => {
            btn.disabled = currentQuestionIndex === 0;
        });
    }
    
    // Initialize question navigation sidebar
    function initializeQuestionNavigation() {
        document.querySelectorAll('.question-number-btn').forEach((btn, index) => {
            btn.addEventListener('click', function() {
                goToQuestion(index);
            });
        });
    }
    
    // Update progress bar and indicators
    function updateProgress() {
        const progressBar = document.querySelector('.bg-blue-600.h-2\\.5');
        const currentQuestionSpan = document.getElementById('current-question');
        const answeredCountSpan = document.getElementById('answered-count');
        const progressPercentage = ((currentQuestionIndex + 1) / totalQuestions) * 100;
        
        progressBar.style.width = progressPercentage + '%';
        
        currentQuestionSpan.textContent = currentQuestionIndex + 1;
        answeredCountSpan.textContent = answeredQuestions.size + ' Answered';
    }
    
    // Update question status indicators (answered, flagged)
    function updateQuestionStatus() {
        document.querySelectorAll('.question-number-btn').forEach((btn, index) => {
            // Reset classes first
            btn.className = 'question-number-btn w-10 h-10 m-1 font-bold flex items-center justify-center rounded';
            
            // Add base classes
            if (index === currentQuestionIndex) {
                btn.classList.add('ring-2', 'ring-blue-500', 'dark:ring-blue-400');
            }
            
            // Answered state
            if (answeredQuestions.has(index)) {
                btn.classList.add('bg-green-600', 'border', 'border-green-600', 'text-white');
            } else {
                btn.classList.add('border', 'border-gray-300', 'dark:border-gray-600', 'text-gray-700', 'dark:text-gray-300', 'hover:bg-gray-100', 'dark:hover:bg-gray-700');
            }
            
            // Flagged state
            if (flaggedQuestions.has(index)) {
                // Add a red dot indicator for flagged questions
                if (!btn.querySelector('.flag-indicator')) {
                    const flagIndicator = document.createElement('span');
                    flagIndicator.className = 'flag-indicator absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full';
                    btn.style.position = 'relative';
                    btn.appendChild(flagIndicator);
                }
            } else {
                // Remove flag indicator if exists
                const flagIndicator = btn.querySelector('.flag-indicator');
                if (flagIndicator) {
                    btn.removeChild(flagIndicator);
                }
            }
        });
        
        // Update sidebar counts
        document.getElementById('sidebar-answered').textContent = answeredQuestions.size;
        document.getElementById('sidebar-unanswered').textContent = totalQuestions - answeredQuestions.size;
        document.getElementById('sidebar-flagged').textContent = flaggedQuestions.size;
    }
    
    // Timer function
    function startTimer() {
        timerInterval = setInterval(updateTimer, 1000);
    }
    
    function updateTimer() {
        timerSeconds++;
        
        const hours = Math.floor(timerSeconds / 3600);
        const minutes = Math.floor((timerSeconds % 3600) / 60);
        const seconds = timerSeconds % 60;
        
        timerDisplay.textContent = 
            (hours < 10 ? '0' + hours : hours) + ':' +
            (minutes < 10 ? '0' + minutes : minutes) + ':' +
            (seconds < 10 ? '0' + seconds : seconds);
        
        // Add warning colors based on time
        if (timerSeconds > 2700) { // 45 minutes - warning
            quizTimer.classList.remove('bg-white', 'bg-opacity-20');
            quizTimer.classList.add('bg-yellow-100', 'text-yellow-800', 'dark:bg-yellow-800', 'dark:text-yellow-100');
        }
        if (timerSeconds > 3300) { // 55 minutes - danger
            quizTimer.classList.remove('bg-yellow-100', 'text-yellow-800', 'dark:bg-yellow-800', 'dark:text-yellow-100');
            quizTimer.classList.add('bg-red-100', 'text-red-800', 'dark:bg-red-800', 'dark:text-red-100', 'animate-pulse');
        }
    }
    
    // Submit quiz function
    function submitQuiz() {
        // Stop the timer
        clearInterval(timerInterval);
        
        const attemptId = document.getElementById('quiz-container').dataset.attemptId;
        const answers = {};
        const completionTime = Math.floor((new Date() - startTime) / 1000);
        
        questions.forEach((question) => {
            const questionId = question.id.split('-')[1];
            const selectedOptions = Array.from(
                question.querySelectorAll('input:checked')
            ).map(input => input.value);
            
            answers[questionId] = selectedOptions;
        });
        
        fetch(`/quiz/submit/${attemptId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                answers: answers,
                completionTime: completionTime
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Create success message element
                const resultMessage = document.createElement('div');
                resultMessage.className = 'p-4 mb-4 text-sm text-green-800 bg-green-100 dark:bg-green-800 dark:text-green-100 rounded-lg';
                resultMessage.innerHTML = `
                    <h4 class="text-lg font-medium mb-2"><i class="fas fa-check-circle mr-2"></i>Quiz Submitted Successfully!</h4>
                    <p>Your answers have been recorded. You'll be redirected to the results page shortly.</p>
                    <div class="mt-3 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                        <div class="bg-green-600 h-2.5 rounded-full w-full"></div>
                    </div>
                `;
                
                document.getElementById('quiz-container').innerHTML = '';
                document.getElementById('quiz-container').appendChild(resultMessage);
                
                // Redirect after a short delay
                setTimeout(() => {
                    window.location.href = `/quiz/results/${attemptId}`;
                }, 3000);
            } else {
                alert('Error submitting quiz: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while submitting the quiz. Please try again.');
        });
    }
});