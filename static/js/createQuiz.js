document.addEventListener('DOMContentLoaded', function () {
    
    // Page navigation
    document.getElementById('nextToPage3').addEventListener('click', function () {
        if (!validateForm()) {
            return;
        }
        document.getElementById('page2').classList.add('hidden');
        document.getElementById('page3').classList.remove('hidden');

        // Add first question automatically if none exist
        if (document.querySelectorAll('.question-block').length === 0) {
            addQuestion();
        }
    });

    document.getElementById('backToPage2').addEventListener('click', function () {
        document.getElementById('page3').classList.add('hidden');
        document.getElementById('page2').classList.remove('hidden');
    });

    // Initialize with page2 visible
    if (document.getElementById('page2')) {
        document.getElementById('page2').classList.remove('hidden');
    }
    if (document.getElementById('page3')) {
        document.getElementById('page3').classList.add('hidden');
    }
    document.getElementById('questionsContainer').innerHTML = '';
    document.getElementById('quizTitle').value = '';
    document.getElementById('quizSubject').value = '';

    // Preview quiz button functionality
    document.getElementById('previewQuiz').addEventListener('click', function () {
        const quizData = generateQuizData();

        if (validateQuizData(quizData)) {
            // Store the quiz data for preview
            localStorage.setItem('previewQuizData', JSON.stringify(quizData));

            // Show preview page
            document.getElementById('page3').classList.add('hidden');
            document.getElementById('page4').classList.remove('hidden');

            // Render preview
            function renderPreview(quizData) {
                // Set basic quiz info
                document.getElementById('previewTitle').textContent = quizData.title;
                document.getElementById('previewSubject').textContent = quizData.subject;
                document.getElementById('questionCount').textContent = quizData.questions.length;

                // Set creation date to today
                const today = new Date();
                document.getElementById('creationDate').textContent = today.toLocaleDateString();

                // Get the container for questions and clear previous content
                const previewContainer = document.getElementById('previewContainer');

                // Remove loading indicator and clear any previous preview content
                document.getElementById('loadingIndicator').classList.add('hidden');

                // Remove any existing question previews (except the loading indicator)
                Array.from(previewContainer.children).forEach(child => {
                    if (child.id !== 'loadingIndicator') {
                        child.remove();
                    }
                });

                // Add legend for correct answers
                const legend = document.createElement('div');
                legend.className = 'bg-white rounded-xl shadow-sm p-4 mb-6 border border-gray-100 flex items-center';
                legend.innerHTML = `
                                    <div class="flex items-center mr-6">
                                        <div class="w-4 h-4 bg-green-500 rounded-sm mr-2"></div>
                                        <span class="text-sm text-gray-600">Correct answer</span>
                                    </div>
                                    <div class="flex items-center">
                                        <div class="w-4 h-4 bg-gray-100 border border-gray-300 rounded-sm mr-2"></div>
                                        <span class="text-sm text-gray-600">Incorrect answer</span>
                                    </div>
                                    `;
                previewContainer.appendChild(legend);

                // Create preview elements for each question
                quizData.questions.forEach((question, qIndex) => {
                    const questionElement = document.createElement('div');
                    questionElement.className = 'bg-white rounded-xl shadow-md p-6 mb-6 border border-gray-100';

                    // Create question header
                    const questionHeader = document.createElement('div');
                    questionHeader.className = 'flex items-center mb-4';
                    questionHeader.innerHTML = `
                                            <div class="bg-indigo-600 text-white rounded-full w-8 h-8a flex items-center justify-center font-bold mr-3">
                                                ${qIndex + 1}
                                            </div>
                                            <h3 class="text-xl font-semibold text-gray-800">${question.text}</h3>
                                        `;

                    questionElement.appendChild(questionHeader);

                    // Add question image if exists
                    if (question.image) {
                        const imageDiv = document.createElement('div');
                        imageDiv.className = 'mb-5 flex justify-center';
                        imageDiv.innerHTML = `<img src="${question.image}" alt="Question Image" class="max-h-60 rounded-lg">`;
                        questionElement.appendChild(imageDiv);
                    }

                    // Create options container
                    const optionsContainer = document.createElement('div');
                    optionsContainer.className = 'ml-11 space-y-3';

                    // Add options
                    question.options.forEach((option, oIndex) => {
                        const optionElement = document.createElement('div');
                        // Highlight correct answers
                        optionElement.className = `flex items-start p-3 rounded-lg border ${option.isCorrect ? 'border-green-300 bg-green-50' : 'border-gray-200'}`;

                        // Create option content with correct checkmark/indicator
                        const optionHTML = `
                <div class="flex-shrink-0 mr-3 mt-1">
                    <div class="w-5 h-5 border rounded-${question.type === 'single' ? 'full' : 'md'} flex items-center justify-center ${option.isCorrect ? 'bg-green-500 border-green-500 text-white' : 'border-gray-400'}">
                        ${option.isCorrect ? '<i class="fas fa-check text-xs"></i>' : ''}
                    </div>
                </div>
                <div class="flex-grow">
                    <p class="text-gray-800">${option.text}</p>
                    ${option.image ? `
                    <div class="mt-2">
                        <img src="${option.image}" alt="Option Image" class="max-h-40 rounded">
                    </div>` : ''}
                </div>
            `;

                        optionElement.innerHTML = optionHTML;
                        optionsContainer.appendChild(optionElement);
                    });

                    questionElement.appendChild(optionsContainer);
                    previewContainer.appendChild(questionElement);
                });
            }
        }
    });

    // Back to editor button in preview
    document.getElementById('backToEdit').addEventListener('click', function () {
        document.getElementById('page4').classList.add('hidden');
        document.getElementById('page3').classList.remove('hidden');
        // Don't reload questions since they're already in the editor
    });


    // Save quiz button in preview
    document.getElementById('saveQuiz').addEventListener('click', function () {
        // Set flag to skip the beforeunload warning
        window.skipBeforeUnloadWarning = true;

        // Get quiz data from localStorage
        const quizData = JSON.parse(localStorage.getItem('previewQuizData'));

        // Submit the form with quiz data
        document.getElementById('quizData').value = JSON.stringify(quizData);

        // Clear localStorage BEFORE submitting the form
        localStorage.removeItem('previewQuizData');

        // Submit the form
        document.getElementById('quizForm').submit();

        
    });

    // Add this to help check if we're coming back after a successful save
    // This should run when the page loads
    document.addEventListener('DOMContentLoaded', function () {
        // Check if there's a success message indicating a quiz was just saved
        const successMessages = document.querySelectorAll('.bg-green-100.text-green-800');
        if (successMessages.length > 0) {
            // If we just saved a quiz successfully, make sure everything is cleared
            localStorage.removeItem('previewQuizData');
            document.getElementById('quizTitle').value = '';
            document.getElementById('quizSubject').value = '';
            document.getElementById('questionsContainer').innerHTML = '';

            // Make sure we're on page 2
            if (document.getElementById('page2')) {
                document.getElementById('page2').classList.remove('hidden');
            }
            if (document.getElementById('page3')) {
                document.getElementById('page3').classList.add('hidden');
            }
            if (document.getElementById('page4')) {
                document.getElementById('page4').classList.add('hidden');
            }
        }
    });

    // Question management functions
    function updateQuestionNumbers() {
        const questions = document.querySelectorAll('.question-block');
        questions.forEach((question, index) => {
            question.querySelector('.question-label').textContent = `Question ${index + 1}`;
        });
    }

    function updateOptionNumbers(optionsContainer) {
        const options = optionsContainer.querySelectorAll('.option-block');
        options.forEach((option, index) => {
            option.querySelector('.option-label').textContent = `Option ${index + 1}:`;
        });
    }

    // Modified addQuestion function to prevent duplication
    function addQuestion() {
        const container = document.getElementById('questionsContainer');
        // Check if this is being called during initialization with saved data
        const isInitialLoad = arguments[0] === 'initialLoad';

        // Only add a question if this isn't part of the initial load of saved data
        // or if there are no questions yet
        if (!isInitialLoad || container.children.length === 0) {
            const questionHTML = `
                <div class="question-block border p-4 rounded-md mt-4 relative bg-indigo-100">
                    <button class="absolute top-2 right-2 text-red-500 remove-question">X</button>
                    <label class="question-label block font-medium">Question ${container.children.length + 1}</label>
                    <textarea class="w-full border p-2 rounded-md mt-2 question-input overflow-hidden" 
                            placeholder="Enter question" rows="1"></textarea>
                    <div class="mt-2">
                        <div class="border-dashed border-2 border-indigo-300 p-6 text-center drop-zone hover:bg-indigo-50 transition cursor-pointer">
                            <p>Drop image here or click to upload</p>
                            <p class="text-xs text-gray-500 mt-1">Supported formats: JPG, PNG, GIF</p>
                            <input type="file" class="hidden file-input" accept="image/*">
                            <div class="image-preview mt-2 hidden"></div>
                        </div>
                    </div>
                    <div class="mt-4">
                        <div class="flex items-center justify-between">
                            <label class="block font-medium">Options</label>
                            <select class="border rounded p-1 text-sm bg-white" title="Question Type">
                                <option value="single">Single Correct Answer</option>
                                <option value="multiple">Multiple Correct Answers</option>
                            </select>
                        </div>
                        <p class="text-xs text-gray-500 mt-1 mb-2">Click on an option to mark it as correct.</p>
                        <button class="mt-1 text-blue-500 add-option">+ Add Option</button>
                        <div class="options-container mt-2"></div>
                    </div>
                </div>`;
            container.insertAdjacentHTML('beforeend', questionHTML);
            updateQuestionNumbers();

            // Add the first option automatically
            const newQuestion = container.lastElementChild;
            addOption(newQuestion.querySelector('.options-container'));

            // Scroll to bottom smoothly
            setTimeout(() => {
                container.lastElementChild.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 200);

            // Initialize the new textarea after it's added
            const newTextarea = container.lastElementChild.querySelector('.question-input');
            if (newTextarea) {
                autoResizeTextarea(newTextarea);
            }
        }
    }

    // Modify the DOMContentLoaded event handler to fix the loading of saved data
    const savedQuizData = localStorage.getItem('previewQuizData');

    if (savedQuizData) {
        const quizData = JSON.parse(savedQuizData);

        // Populate the quiz title and subject
        document.getElementById('quizTitle').value = quizData.title || '';
        document.getElementById('quizSubject').value = quizData.subject || '';

        // Clear existing questions first to prevent duplication
        document.getElementById('questionsContainer').innerHTML = '';

        // If we have questions, switch to the questions page and load them
        if (quizData.questions && quizData.questions.length > 0) {
            document.getElementById('page2').classList.add('hidden');
            document.getElementById('page3').classList.remove('hidden');

            // Load each question
            quizData.questions.forEach(question => {
                addQuestion('initialLoad'); // Pass flag to indicate this is initial load
                const questionBlocks = document.querySelectorAll('.question-block');
                const currentQuestion = questionBlocks[questionBlocks.length - 1];

                // Set question text
                currentQuestion.querySelector('.question-input').value = question.text;

                // Set question type
                currentQuestion.querySelector('select').value = question.type;

                // Set question image if exists
                if (question.image) {
                    const imagePreview = currentQuestion.querySelector('.image-preview');
                    imagePreview.classList.remove('hidden');

                    // Create and add image
                    const img = document.createElement('img');
                    img.classList.add('max-h-40', 'mx-auto');
                    img.src = question.image;

                    // Create remove button
                    const removeBtn = document.createElement('button');
                    removeBtn.textContent = 'Remove Image';
                    removeBtn.classList.add('mt-2', 'text-red-500', 'text-sm');
                    removeBtn.onclick = function (e) {
                        e.stopPropagation();
                        imagePreview.classList.add('hidden');
                        imagePreview.innerHTML = '';
                        currentQuestion.querySelector('.drop-zone p').classList.remove('hidden');
                        currentQuestion.querySelector('.drop-zone .text-xs').classList.remove('hidden');
                        currentQuestion.querySelector('.file-input').value = '';
                    };

                    // Add elements to preview
                    imagePreview.innerHTML = '';
                    imagePreview.appendChild(img);
                    imagePreview.appendChild(removeBtn);

                    // Hide upload text
                    currentQuestion.querySelector('.drop-zone p').classList.add('hidden');
                    currentQuestion.querySelector('.drop-zone .text-xs').classList.add('hidden');
                }

                // Clear default options first
                const optionsContainer = currentQuestion.querySelector('.options-container');
                optionsContainer.innerHTML = '';

                // Add each option
                question.options.forEach(option => {
                    addOption(optionsContainer);
                    const optionBlocks = optionsContainer.querySelectorAll('.option-block');
                    const currentOption = optionBlocks[optionBlocks.length - 1];

                    // Set option text
                    currentOption.querySelector('input[type="text"]').value = option.text;

                    // Set option correctness and apply styling
                    const correctToggle = currentOption.querySelector('.correct-option');
                    correctToggle.checked = option.isCorrect;

                    // Apply visual feedback for correct answer
                    if (option.isCorrect) {
                        currentOption.classList.add('border-green-500', 'border-2');
                    }

                    // Set option image if exists
                    if (option.image) {
                        const optionImagePreview = currentOption.querySelector('.option-image-preview');
                        optionImagePreview.classList.remove('hidden');

                        // Create and add image
                        const img = document.createElement('img');
                        img.classList.add('max-h-32', 'mx-auto');
                        img.src = option.image;

                        // Create remove button
                        const removeBtn = document.createElement('button');
                        removeBtn.textContent = 'Remove';
                        removeBtn.classList.add('mt-1', 'text-red-500', 'text-xs');
                        removeBtn.onclick = function (e) {
                            e.stopPropagation();
                            optionImagePreview.classList.add('hidden');
                            optionImagePreview.innerHTML = '';
                            currentOption.querySelector('.option-drop-zone p').classList.remove('hidden');
                            currentOption.querySelector('.option-file-input').value = '';
                        };

                        // Add elements to preview
                        optionImagePreview.innerHTML = '';
                        optionImagePreview.appendChild(img);
                        optionImagePreview.appendChild(removeBtn);

                        // Hide upload text
                        currentOption.querySelector('.option-drop-zone p').classList.add('hidden');
                    }
                });
            });
        }
    }


    function addOption(optionsContainer) {
        const questionType = optionsContainer.closest('.question-block').querySelector('select').value;
        const inputType = questionType === 'single' ? 'radio' : 'checkbox';
        const name = `question-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

        const optionHTML = `
            <div class="option-block border border-gray-200 rounded-lg p-3 mt-3 bg-white hover:border-indigo-300 transition">
                <div class="flex items-start">
                    <div class="correct-toggle cursor-pointer mr-3 mt-1">
                        <input type="${inputType}" name="${name}" class="correct-option">
                    </div>
                    <div class="flex-grow">
                        <div class="flex items-center justify-between">
                            <label class="option-label font-medium">Option ${optionsContainer.children.length + 1}:</label>
                            <button class="text-red-500 remove-option">X</button>
                        </div>
                        <input type="text" class="w-full border p-2 rounded-md mt-1" placeholder="Enter option text" />
                        
                        <div class="mt-2">
                            <div class="border-dashed border-2 border-gray-300 p-4 text-center option-drop-zone hover:bg-gray-50 transition cursor-pointer">
                                <p class="text-sm">Add image to option (optional)</p>
                                <input type="file" class="hidden option-file-input" accept="image/*">
                                <div class="option-image-preview mt-2 hidden"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`;
        optionsContainer.insertAdjacentHTML('beforeend', optionHTML);
        updateOptionNumbers(optionsContainer);
    }

    // Setup event listeners for adding questions
    document.getElementById('addQuestion').addEventListener('click', addQuestion);

    document.addEventListener('click', function (event) {
        // Handle add option button
        if (event.target.classList.contains('add-option')) {
            const optionsContainer = event.target.nextElementSibling;
            addOption(optionsContainer);
        }
        // Handle remove option button
        else if (event.target.classList.contains('remove-option')) {
            const optionsContainer = event.target.closest('.options-container');
            event.target.closest('.option-block').remove();
            updateOptionNumbers(optionsContainer);
        }
        // Handle remove question button
        else if (event.target.classList.contains('remove-question')) {
            event.target.closest('.question-block').remove();
            updateQuestionNumbers();
        }
        // Handle clicking on the correct toggle area
        else if (event.target.classList.contains('correct-toggle') ||
            (event.target.parentElement && event.target.parentElement.classList.contains('correct-toggle'))) {
            const toggle = event.target.classList.contains('correct-toggle') ?
                event.target : event.target.parentElement;
            const inputEl = toggle.querySelector('input');
            inputEl.checked = !inputEl.checked;

            // Apply visual feedback for correct answer
            const optionBlock = toggle.closest('.option-block');
            if (inputEl.checked) {
                optionBlock.classList.add('border-green-500', 'border-2');
            } else {
                optionBlock.classList.remove('border-green-500', 'border-2');
            }

            // For radio buttons, uncheck others
            if (inputEl.type === 'radio' && inputEl.checked) {
                const name = inputEl.name;
                document.querySelectorAll(`input[name="${name}"]`).forEach(radio => {
                    if (radio !== inputEl) {
                        radio.checked = false;
                        radio.closest('.option-block').classList.remove('border-green-500', 'border-2');
                    }
                });
            }
        }
        // Handle option drop zone clicks
        else if (event.target.closest('.option-drop-zone')) {
            const dropZone = event.target.closest('.option-drop-zone');
            dropZone.querySelector('.option-file-input').click();
        }
    });

    // Handle question type changes
    document.addEventListener('change', function (event) {
        if (event.target.tagName === 'SELECT' && event.target.closest('.question-block')) {
            const questionBlock = event.target.closest('.question-block');
            const optionsContainer = questionBlock.querySelector('.options-container');
            const newType = event.target.value;
            const name = `question-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

            // Update all input types in this question
            optionsContainer.querySelectorAll('.correct-option').forEach(input => {
                // Save checked state
                const wasChecked = input.checked;

                // Replace with new input type
                const newInput = document.createElement('input');
                newInput.type = newType === 'single' ? 'radio' : 'checkbox';
                newInput.className = 'correct-option';
                newInput.name = name;
                newInput.checked = wasChecked;

                // Replace old input
                input.parentNode.replaceChild(newInput, input);
            });
        }
        // Handle file selection for options
        else if (event.target.classList.contains('option-file-input')) {
            const file = event.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const dropZone = event.target.closest('.option-drop-zone');
                displayOptionImage(dropZone, file);
            }
        }
        // Handle file selection for questions
        else if (event.target.classList.contains('file-input')) {
            handleFileSelect(event);
        }
    });

    // Auto-resize textarea function
    function autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }

    // Event listener for auto-resizing textareas
    document.addEventListener('input', function (event) {
        if (event.target.classList.contains('question-input')) {
            autoResizeTextarea(event.target);
        }
    });

    // Handle drag-and-drop for questions
    if (document.getElementById('questionsContainer')) {
        document.getElementById('questionsContainer').addEventListener('dragover', function (event) {
            const dropZone = event.target.closest('.drop-zone, .option-drop-zone');
            if (dropZone) {
                event.preventDefault();
                dropZone.classList.add('border-indigo-500');
            }
        });

        document.getElementById('questionsContainer').addEventListener('dragleave', function (event) {
            const dropZone = event.target.closest('.drop-zone, .option-drop-zone');
            if (dropZone) {
                dropZone.classList.remove('border-indigo-500');
            }
        });

        document.getElementById('questionsContainer').addEventListener('drop', function (event) {
            const dropZone = event.target.closest('.drop-zone, .option-drop-zone');
            if (dropZone) {
                event.preventDefault();
                dropZone.classList.remove('border-indigo-500');

                const file = event.dataTransfer.files[0];
                if (file && file.type.startsWith('image/')) {
                    if (dropZone.classList.contains('option-drop-zone')) {
                        displayOptionImage(dropZone, file);
                    } else {
                        displayImage(dropZone, file);
                    }
                }
            }
        });
    }

    // Function to handle file selection for questions
    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (file && file.type.startsWith('image/')) {
            const dropZone = event.target.closest('.drop-zone');
            displayImage(dropZone, file);
        }
    }

function displayImage(dropZone, file) {
    const preview = dropZone.querySelector('.image-preview');
    preview.innerHTML = '';
    preview.classList.remove('hidden');
    
    // Show loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.textContent = 'Uploading image...';
    loadingIndicator.classList.add('text-indigo-500', 'text-center', 'py-2');
    preview.appendChild(loadingIndicator);
    
    // Hide the upload text
    dropZone.querySelector('p').classList.add('hidden');
    dropZone.querySelector('.text-xs').classList.add('hidden');
    
    // Upload the image to server first
    const formData = new FormData();
    formData.append('image', file);
    
    fetch('/quiz/upload_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading indicator
        preview.innerHTML = '';
        
        if (data.success) {
            // Create image element
            const img = document.createElement('img');
            img.classList.add('max-h-40', 'mx-auto');
            img.src = data.url; // Use the URL returned from server
            
            // Create remove button
            const removeBtn = document.createElement('button');
            removeBtn.textContent = 'Remove Image';
            removeBtn.classList.add('mt-2', 'text-red-500', 'text-sm');
            removeBtn.onclick = function (e) {
                e.stopPropagation();
                preview.classList.add('hidden');
                preview.innerHTML = '';
                dropZone.querySelector('p').classList.remove('hidden');
                dropZone.querySelector('.text-xs').classList.remove('hidden');
                // Reset file input
                dropZone.querySelector('.file-input').value = '';
            };
            
            preview.appendChild(img);
            preview.appendChild(removeBtn);
        } else {
            // Show error
            preview.innerHTML = `<div class="text-red-500 text-center">Upload failed: ${data.message}</div>`;
            // Show upload text again
            dropZone.querySelector('p').classList.remove('hidden');
            dropZone.querySelector('.text-xs').classList.remove('hidden');
        }
    })
    .catch(error => {
        preview.innerHTML = '<div class="text-red-500 text-center">Upload failed</div>';
        console.error('Error:', error);
        // Show upload text again
        dropZone.querySelector('p').classList.remove('hidden');
        dropZone.querySelector('.text-xs').classList.remove('hidden');
    });
}

function displayOptionImage(dropZone, file) {
    const preview = dropZone.querySelector('.option-image-preview');
    preview.innerHTML = '';
    preview.classList.remove('hidden');
    
    // Show loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.textContent = 'Uploading...';
    loadingIndicator.classList.add('text-indigo-500', 'text-center', 'py-1', 'text-sm');
    preview.appendChild(loadingIndicator);
    
    // Hide the upload text
    dropZone.querySelector('p').classList.add('hidden');
    
    // Upload the image to server first
    const formData = new FormData();
    formData.append('image', file);
    
    fetch('/quiz/upload_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading indicator
        preview.innerHTML = '';
        
        if (data.success) {
            // Create image element
            const img = document.createElement('img');
            img.classList.add('max-h-32', 'mx-auto');
            img.src = data.url; // Use the URL returned from server
            
            // Create remove button
            const removeBtn = document.createElement('button');
            removeBtn.textContent = 'Remove';
            removeBtn.classList.add('mt-1', 'text-red-500', 'text-xs');
            removeBtn.onclick = function (e) {
                e.stopPropagation();
                preview.classList.add('hidden');
                preview.innerHTML = '';
                dropZone.querySelector('p').classList.remove('hidden');
                // Reset file input
                dropZone.querySelector('.option-file-input').value = '';
            };
            
            preview.appendChild(img);
            preview.appendChild(removeBtn);
        } else {
            // Show error
            preview.innerHTML = `<div class="text-red-500 text-xs text-center">Failed: ${data.message}</div>`;
            // Show upload text again
            dropZone.querySelector('p').classList.remove('hidden');
        }
    })
    .catch(error => {
        preview.innerHTML = '<div class="text-red-500 text-xs text-center">Upload failed</div>';
        console.error('Error:', error);
        // Show upload text again
        dropZone.querySelector('p').classList.remove('hidden');
    });
}

    // Function to generate quiz data from the form
    function generateQuizData() {
        const quizData = {
            title: document.getElementById('quizTitle').value,
            subject: document.getElementById('quizSubject').value,
            questions: []
        };

        // Gather all questions and options
        const questionBlocks = document.querySelectorAll('.question-block');

        questionBlocks.forEach((questionBlock) => {
            const questionText = questionBlock.querySelector('.question-input').value;
            const questionType = questionBlock.querySelector('select').value;

            // Get question image if exists
            let questionImage = null;
            const imgPreview = questionBlock.querySelector('.image-preview img');
            if (imgPreview) {
                questionImage = imgPreview.src;
            }

            const options = [];
            const optionBlocks = questionBlock.querySelectorAll('.option-block');

            optionBlocks.forEach((optionBlock) => {
                const optionText = optionBlock.querySelector('input[type="text"]').value;
                const isCorrect = optionBlock.querySelector('.correct-option').checked;

                // Get option image if exists
                let optionImage = null;
                const optImgPreview = optionBlock.querySelector('.option-image-preview img');
                if (optImgPreview) {
                    optionImage = optImgPreview.src;
                }

                options.push({
                    text: optionText,
                    isCorrect: isCorrect,
                    image: optionImage
                });
            });

            quizData.questions.push({
                text: questionText,
                type: questionType,
                image: questionImage,
                options: options
            });
        });

        return quizData;
    }

    // Function to validate the quiz data
    function validateQuizData(quizData) {
        if (!quizData.title) {
            alert('Please enter a quiz title');
            return false;
        }

        if (quizData.questions.length === 0) {
            alert('Please add at least one question');
            return false;
        }

        for (let i = 0; i < quizData.questions.length; i++) {
            const question = quizData.questions[i];

            if (!question.text) {
                alert(`Please enter text for question ${i + 1}`);
                return false;
            }

            if (question.options.length < 2) {
                alert(`Please add at least two options for question ${i + 1}`);
                return false;
            }

            let hasCorrectOption = false;
            for (let j = 0; j < question.options.length; j++) {
                const option = question.options[j];

                if (!option.text) {
                    alert(`Please enter text for option ${j + 1} in question ${i + 1}`);
                    return false;
                }

                if (option.isCorrect) {
                    hasCorrectOption = true;
                }
            }

            if (!hasCorrectOption) {
                alert(`Please mark at least one correct answer for question ${i + 1}`);
                return false;
            }
        }

        return true;
    }

    // Add keyboard shortcuts for common actions
    document.addEventListener('keydown', function (event) {
        // Ctrl+Enter to add a new question
        if (event.ctrlKey && event.key === 'Enter' && document.getElementById('page3') && !document.getElementById('page3').classList.contains('hidden')) {
            event.preventDefault();
            addQuestion();
        }
    });

    // Add form validation for required fields
    function validateForm() {
        const title = document.getElementById("quizTitle").value;
        const subject = document.getElementById("quizSubject").value;

        if (!title) {
            alert("Please enter a quiz title");
            return false;
        }

        if (!subject) {
            alert("Please enter a subject");
            return false;
        }

        return true;
    }

    // Preview quiz button functionality
    document.getElementById('previewQuiz').addEventListener('click', function () {
        const quizData = generateQuizData();

        if (validateQuizData(quizData)) {
            // Store the quiz data for preview
            localStorage.setItem('previewQuizData', JSON.stringify(quizData));

            // Show preview page
            document.getElementById('page3').classList.add('hidden');
            document.getElementById('page4').classList.remove('hidden');

            // Clear previous preview content
            const previewContainer = document.getElementById('previewContainer');
            // Keep the loading indicator but remove everything else
            Array.from(previewContainer.children).forEach(child => {
                if (child.id !== 'loadingIndicator') {
                    child.remove();
                }
            });
            // Show loading indicator (just in case it was hidden)
            document.getElementById('loadingIndicator').classList.remove('hidden');

            // Call renderPreview with the quiz data - with a slight delay to show the loading animation
            setTimeout(() => {
                renderPreview(quizData);
            }, 300);
        }
    });

    window.addEventListener('beforeunload', function (e) {
        // Skip the warning if we're intentionally navigating away
        if (window.skipBeforeUnloadWarning) {
            return;
        }

        const hasQuestions = document.querySelectorAll(".question-block").length > 0;
        const hasTitle = document.getElementById("quizTitle") && document.getElementById("quizTitle").value.trim() !== '';

        if (hasQuestions || hasTitle) {
            e.preventDefault();
            e.returnValue = '';
            return '';
        }
    });

    function renderPreview(quizData) {
        // Set basic quiz info
        document.getElementById('previewTitle').textContent = quizData.title;
        document.getElementById('previewSubject').textContent = quizData.subject;
        document.getElementById('questionCount').textContent = quizData.questions.length;

        // Set creation date to today
        const today = new Date();
        document.getElementById('creationDate').textContent = today.toLocaleDateString();

        // Get the container for questions
        const previewContainer = document.getElementById('previewContainer');

        // Hide loading indicator
        document.getElementById('loadingIndicator').classList.add('hidden');

        // Clear previous preview content (except loading indicator)
        Array.from(previewContainer.children).forEach(child => {
            if (child.id !== 'loadingIndicator') {
                child.remove();
            }
        });

        // Add legend for correct answers FIRST, before adding the questions
        const legend = document.createElement('div');
        legend.className = 'bg-white rounded-xl shadow-sm p-4 mb-6 border border-gray-100 flex items-center';
        legend.innerHTML = `
        <div class="flex items-center mr-6">
            <div class="w-4 h-4 bg-green-500 rounded-sm mr-2"></div>
            <span class="text-sm text-gray-600">Correct answer</span>
        </div>
        <div class="flex items-center">
            <div class="w-4 h-4 bg-gray-100 border border-gray-300 rounded-sm mr-2"></div>
            <span class="text-sm text-gray-600">Incorrect answer</span>
        </div>
    `;
        previewContainer.appendChild(legend);

        // Create preview elements for each question
        quizData.questions.forEach((question, qIndex) => {
            const questionElement = document.createElement('div');
            questionElement.className = 'bg-white rounded-xl shadow-md p-6 mb-6 border border-gray-100';

            // Create question header
            const questionHeader = document.createElement('div');
            questionHeader.className = 'flex items-center mb-4';
            questionHeader.innerHTML = `
            <div class="bg-indigo-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold mr-3">
                ${qIndex + 1}
            </div>
            <h3 class="text-xl font-semibold text-gray-800">${question.text}</h3>
        `;

            questionElement.appendChild(questionHeader);

            // Add question image if exists
            if (question.image) {
                const imageDiv = document.createElement('div');
                imageDiv.className = 'mb-5 flex justify-center';
                imageDiv.innerHTML = `<img src="${question.image}" alt="Question Image" class="max-h-60 rounded-lg">`;
                questionElement.appendChild(imageDiv);
            }

            // Create options container
            const optionsContainer = document.createElement('div');
            optionsContainer.className = 'ml-11 space-y-3';

            // Add options
            question.options.forEach((option, oIndex) => {
                const optionElement = document.createElement('div');
                optionElement.className = `flex items-start p-3 rounded-lg border ${option.isCorrect ? 'border-green-300 bg-green-50' : 'border-gray-200'}`;

                // Create option content
                let optionHTML = `
                <div class="flex-shrink-0 mr-3 mt-1">
                    <div class="w-5 h-5 border rounded-${question.type === 'single' ? 'full' : 'md'} flex items-center justify-center ${option.isCorrect ? 'bg-green-500 border-green-500 text-white' : 'border-gray-400'}">
                        ${option.isCorrect ? '<i class="fas fa-check text-xs"></i>' : ''}
                    </div>
                </div>
                <div class="flex-grow">
                    <p class="text-gray-800">${option.text}</p>
            `;

                // Add option image if exists
                if (option.image) {
                    optionHTML += `
                    <div class="mt-2">
                        <img src="${option.image}" alt="Option Image" class="max-h-40 rounded">
                    </div>
                `;
                }

                optionHTML += '</div>';
                optionElement.innerHTML = optionHTML;

                optionsContainer.appendChild(optionElement);
            });

            questionElement.appendChild(optionsContainer);
            previewContainer.appendChild(questionElement);
        });
    }

});