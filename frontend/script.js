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
                    await eel.prepare_quiz_data()();
                    console.log('Answer saved to Python backend');
                } catch (error) {
                    console.error('Error saving to backend:', error);
                }
                // -------------------------------------------------------

                // incorrect answer because if it aint correct its incorrect
            } else {
                resultDiv.textContent = 'Incorrect. The correct answer is Random Access Memory.';
                resultDiv.className = 'result show incorrect';
            }
                //--------------------------------------------------------
          
        }


