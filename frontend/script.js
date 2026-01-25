// ----------------------------------------------------------------------------------------------
// Signup  handling
// ----------------------------------------------------------------------------------------------

async function handleSignup() {
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    // Send data to Python backend
    const result = await eel.signup(username, email, password)();
    
    const messageDiv = document.getElementById('message');
    messageDiv.classList.remove('hidden', 'success', 'error');
    messageDiv.textContent = result.message;
    
    if (result.success) {
        messageDiv.classList.add('success');
        // Clear form on success
        document.getElementById('username').value = '';
        document.getElementById('email').value = '';
        document.getElementById('password').value = '';
        
        // Redirect to login 
        eel.navigate_to_login()
    } else {
        messageDiv.classList.add('error');
    }
}

function goToLogin() {
    eel.navigate_to_login();
}

// Enter key shortcut for signup
document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        handleSignup();
    }
});
// ----------------------------------------------------------------------------------------------
// Login handling
//-----------------------------------------------------------------------------------------------

async function handleLogin() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    // Send data to Python backend
    const result = await eel.login(username, password)();
    
    const messageDiv = document.getElementById('message');
    messageDiv.classList.remove('hidden', 'success', 'error');
    messageDiv.textContent = result.message;
    
    if (result.success) {
    messageDiv.classList.add('success');
    
    // Redirect to homepage
    eel.navigate_to_homepage();
} else {
    messageDiv.classList.add('error');
}
}

function goToSignup() {
    eel.navigate_to_signup();
}

// Enter key shortcut for login
document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        handleLogin();
    }
});
//----------------------------------------------------------------------------------------------
// Quiz navigation handling
//----------------------------------------------------------------------------------------------


function GoToPage(pageName) {
            window.location.href = pageName + '.html';   //once button clicked, quiz1 + .html... takes too quiz1.html
        }

const quiz1 = document.getElementById("quiz1")
quiz1.addEventListener("click", () => {
    GoToPage('quiz1')
})

const quiz2 = document.getElementById('quiz2')
quiz2.addEventListener("click", () => {
    GoToPage('quiz2')
})


// ----------------------------------------------------------------------------------------------

async function checkAnswer() { //Will check if answer is correct!!!!
            const correctAnswer = 'b';
            const selectedAnswer = document.querySelector('input[name="q1"]:checked');
            
            
            
            //Will need to check if an answer is actually selected
            if (!selectedAnswer) {
                alert('Please select an answer');
                return;
            }
            //----------------------------------------------------
            const isCorrect = selectedAnswer.value === correctAnswer;
            const resultDiv = document.getElementById('result');
            //gets correct answer variable from selected answer === correct answer value
            
            if (isCorrect) {
                resultDiv.textContent = 'Correct! Well done!';
                resultDiv.className = 'result show correct';
                
                // sends data to python 
                try {
                    await eel.prepare_quiz_data(true)();
                    console.log('Answer saved to Python backend');
                } catch (error) {
                    console.error('Error saving to backend:', error);
                }
                // -------------------------------------------------------

                // incorrect answer because if it aint correct its incorrect
                } else {
                    resultDiv.textContent = 'Incorrect. The correct answer is Random Access Memory.';
                    resultDiv.className = 'result show incorrect';
                    
                    // sends data to python as incorrect answer 
                        try {
                            await eel.prepare_quiz_data(false)();
                            console.log('Answer saved to Python backend');
                        } catch (error) {
                            console.error('Error saving to backend:', error);
                        }
                    }
                }

// ----------------------------------------------------------------------------------------------