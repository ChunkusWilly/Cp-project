let currentQuestions = [];

// Load and display questions when page loads
window.onload = async function() {
    const questions = await eel.load_questions()();
    currentQuestions = questions;
    displayQuestions(questions);
    
    // Load and display statistics for each question
    await updateAllQuestionStats();
};

function displayQuestions(questions) {
    const container = document.getElementById('quiz-container');
    
    if (questions.length === 0) {
        container.innerHTML = '<p>No questions available.</p>';
        return;
    }

    questions.forEach((q, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'question';
        questionDiv.innerHTML = `
            <h3>Question ${index + 1}: ${q.question}</h3>
            <div class="question-stats" id="stats-${index}"></div>
        `;
        
        q.options.forEach((option, optionIndex) => {
            const optionLabel = document.createElement('label');
            optionLabel.className = 'option';
            optionLabel.innerHTML = `
                <input type="radio" name="question${index}" value="${optionIndex}">
                ${option}
            `;
            questionDiv.appendChild(optionLabel);
        });
        
        // Add submit button for each question
        const submitButton = document.createElement('button');
        submitButton.textContent = 'Submit Answer';
        submitButton.className = 'submit-btn';
        submitButton.id = `submit-${index}`;
        submitButton.onclick = () => submitAnswer(index);
        questionDiv.appendChild(submitButton);
        
        // Add result div for each question
        const resultDiv = document.createElement('div');
        resultDiv.id = `result-${index}`;
        resultDiv.className = 'result';
        questionDiv.appendChild(resultDiv);
        
        container.appendChild(questionDiv);
    });
}

async function submitAnswer(questionIndex) {
    const selectedAnswer = document.querySelector(`input[name="question${questionIndex}"]:checked`);
    const resultDiv = document.getElementById(`result-${questionIndex}`);
    const submitButton = document.getElementById(`submit-${questionIndex}`);
    
    // Check if an answer is selected
    if (!selectedAnswer) {
        alert('Please select an answer');
        return;
    }
    
    const selectedValue = parseInt(selectedAnswer.value);
    const correctAnswer = currentQuestions[questionIndex].correctAnswer;
    const isCorrect = selectedValue === correctAnswer;
    
    // Display result
    if (isCorrect) {
        resultDiv.textContent = 'Correct! Well done!';
        resultDiv.className = 'result show correct';
    } else {
        resultDiv.textContent = `Incorrect. The correct answer is: ${currentQuestions[questionIndex].options[correctAnswer]}`;
        resultDiv.className = 'result show incorrect';
    }
    
    // Send answer to Python backend with question index
    await eel.prepare_quiz_data(isCorrect, questionIndex)();
    
    // Update stats for this specific question
    await updateQuestionStats(questionIndex);
    
    // Disable the radio buttons and submit button after submission
    const radioButtons = document.querySelectorAll(`input[name="question${questionIndex}"]`);
    radioButtons.forEach(radio => radio.disabled = true);
    submitButton.disabled = true;
}

async function updateQuestionStats(questionIndex) {
    const stats = await eel.get_question_stats(questionIndex)();
    const statsDiv = document.getElementById(`stats-${questionIndex}`);
    
    if (statsDiv && stats.attempts > 0) {
        statsDiv.innerHTML = `
            <small>Attempts: ${stats.attempts} | 
            Correct: ${stats.correct} | 
            Success Rate: ${stats.percentage}%</small>
        `;
    }
}

async function updateAllQuestionStats() {
    const allStats = await eel.get_all_question_stats()();
    
    for (const [index, stats] of Object.entries(allStats)) {
        const statsDiv = document.getElementById(`stats-${index}`);
        if (statsDiv && stats.attempts > 0) {
            statsDiv.innerHTML = `
                <small>Attempts: ${stats.attempts} | 
                Correct: ${stats.correct} | 
                Success Rate: ${stats.percentage}%</small>
            `;
        }
    }
}

async function resetStats() {
    await eel.reset_statistics()();
    location.reload();
}