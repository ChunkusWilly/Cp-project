// ============================================================
//  quiz.js  — Quiz frontend 
// ============================================================


// ── Session configuration ────────────────────────────────────

// Total number of questions to show before ending the quiz session
var TOTAL_ROUNDS = 15;


// ── Session state ────────────────────────────────────────────

// Tracks which round (0-indexed) the user is currently on
// Incremented by goNext() after each question is answered
var currentRound = 0;

// Running count of correct answers given so far in this session
var score = 0;

// The list index of the question currently being displayed
// Sent back to Python with submit_answer() to identify which weight to update
var currentIndex = null;

// The type of the question currently on screen: 'multiple_choice' or 'fill_blank'
// Used by submitAnswer() to decide which input method to read from
var currentType = null;

// Guard flag — set to true as soon as the user submits an answer
// Prevents the submit button from being triggered twice on the same question
var hasAnswered = false;


// ── Boot sequence ─────────────────────────────────────────────

window.addEventListener('load', function () {
    // Wait 150ms after the page loads before making any eel calls
    // This gives eel time to complete its internal WebSocket handshake
    // Calling Python functions before this is ready causes silent failures
    setTimeout(async function () {
        console.log('Calling load_questions…');
        // Tell Python to load quiz_data.json and initialise all weights
        // We await it fully before proceeding so questions are ready
        await eel.load_questions()();
        console.log('load_questions done — loading first question…');
        // Now that questions are loaded on the backend, request the first one
        await loadQuestion();
    }, 150);
});


// ── Load and render a question ───────────────────────────────

async function loadQuestion() {
    // Reset all per-question state variables before building the new card
    hasAnswered  = false;
    currentType  = null;
    currentIndex = null;

    // Request the next question from Python's weighted random selector
    // Python decides which question to show based on current weights
    var q = await eel.get_next_question()();

    // If Python returned null (e.g. weights were never populated), show an error
    // stop here rather than trying to render an empty card
    if (!q) {
        document.getElementById('quiz-area').innerHTML =
            '<p style="color:red">Could not load question — check terminal for errors.</p>';
        return;
    }

    // Store the question index and type so submitAnswer() can use them later
    currentIndex = q.index;
    currentType  = q.type;   // 'multiple_choice' / 'fill_blank'

    // Update the round counter label — currentRound is 0-indexed so we add 1
    // for the human-readable display ("Question 1 of 8", "Question 2 of 8", etc.)
    document.getElementById('round-lbl').textContent =
        'Question ' + (currentRound + 1) + ' of ' + TOTAL_ROUNDS;

    // Clear any previous question card from the DOM before rendering the new one
    var area = document.getElementById('quiz-area');
    area.innerHTML     = '';
    area.style.display = 'block';

    // Create the main card container that holds all question elements
    var card = document.createElement('div');
    card.className = 'card';

    // ── Question text ──────────────────────────────────────
    // Render the question string as a heading inside the card
    var qText = document.createElement('h3');
    qText.textContent = q.question;
    card.appendChild(qText);

    // ── Type badge ─────────────────────────────────────────
    // Show a small label so the user knows whether this is MC or fill-blank
    var badge = document.createElement('span');
    badge.className   = 'type-badge type-' + (q.type === 'fill_blank' ? 'fill' : 'mc');
    badge.textContent = q.type === 'fill_blank' ? 'Fill in the Blank' : 'Multiple Choice';
    card.appendChild(badge);

    // ── Input area ─────────────────────────────────────────
    
    if (q.type === 'fill_blank') {
        renderFillBlank(card, q);
    } else {
        renderMultipleChoice(card, q);
    }

    // ── Feedback div ───────────────────────────────────────
   
    var resultDiv = document.createElement('div');
    resultDiv.id        = 'result';
    resultDiv.className = 'result';
    card.appendChild(resultDiv);

    // ── Submit button ──────────────────────────────────────
  
    var submitBtn = document.createElement('button');
    submitBtn.id          = 'submit-btn';
    submitBtn.className   = 'submit-btn';
    submitBtn.textContent = 'Submit Answer';
    submitBtn.onclick     = submitAnswer;
    card.appendChild(submitBtn);

    // ── Next button ────────────────────────────────────────
   
    var nextBtn = document.createElement('button');
    nextBtn.id            = 'next-btn';
    nextBtn.className     = 'submit-btn next-btn';
    nextBtn.style.display = 'none';
    nextBtn.textContent   = currentRound < TOTAL_ROUNDS - 1 ? 'Next Question →' : 'See Results →';
    nextBtn.onclick       = goNext;
    card.appendChild(nextBtn);

   
    area.appendChild(card);

   
    if (q.type === 'fill_blank') {
        var inp = document.getElementById('fill-input');
        if (inp) inp.focus();
    }
}


// ── Render helpers ───────────────────────────────────────────

function renderMultipleChoice(card, q) {
    // Wrap all the radio button options in a single container div
    // so we can query it later with document.querySelector('.options-group')
    var optGroup = document.createElement('div');
    optGroup.className = 'options-group';

    // Create one labelled radio button for each answer option in the question
    q.options.forEach(function (opt, i) {
        var lbl = document.createElement('label');
        lbl.className = 'option';
        lbl.id        = 'opt-' + i;   // ID used by highlightOptions() later
        lbl.innerHTML = '<input type="radio" name="ans" value="' + i + '"> ' + opt;
        optGroup.appendChild(lbl);
    });

    // Store the correct answer index as a data attribute on the container
    // submitAnswer() reads this back to check whether the user's selection was right
    optGroup.dataset.correct = q.correctAnswer;
    card.appendChild(optGroup);
}

function renderFillBlank(card, q) {
    // Store the canonical display answer on the card element itself
    // This is used by showFeedback() to tell the user the correct answer
    // when they get it wrong — the full acceptedAnswers list stays in Python
    card.dataset.correctDisplay = q.correctAnswer;

    var wrapper = document.createElement('div');
    wrapper.className = 'fill-wrapper';

    // Build the single-line text input the user types their answer into
    var inp = document.createElement('input');
    inp.type         = 'text';
    inp.id           = 'fill-input';
    inp.className    = 'fill-input';
    inp.placeholder  = 'Type your answer…';
    inp.autocomplete = 'off';   // Disable browser autocomplete to avoid hints

    // Allow the user to press Enter as an alternative to clicking Submit
    // This makes keyboard-only navigation smoother
    inp.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') submitAnswer();
    });

    wrapper.appendChild(inp);
    card.appendChild(wrapper);
}


// ── Answer submission ────────────────────────────────────────

async function submitAnswer() {
    // Prevent double-submission — if the user somehow triggers this twice
    // (e.g. double-click or Enter + click), we exit early on the second call
    if (hasAnswered) return;

    var isCorrect = false;

    if (currentType === 'fill_blank') {
        var inp = document.getElementById('fill-input');

        // Require a non-empty answer before allowing submission
        if (!inp || inp.value.trim() === '') {
            alert('Please type an answer!');
            return;
        }

        // Set the flag and disable the input to lock in the answer
        hasAnswered  = true;
        inp.disabled = true;

        // Send the answer to Python for server-side validation
        // Python compares against the full acceptedAnswers list (case-insensitive)
        // We never expose that list to the browser, so the user can't cheat
        isCorrect = await eel.check_fill_blank_answer(currentIndex, inp.value.trim())();

    } else {
        // For multiple choice, check that the user has selected a radio button
        var selected = document.querySelector('input[name="ans"]:checked');
        if (!selected) {
            alert('Please pick an answer!');
            return;
        }

        hasAnswered = true;

        // Read the index of the selected option and the stored correct index
        var chosen  = parseInt(selected.value);
        var correct = parseInt(document.querySelector('.options-group').dataset.correct);
        isCorrect   = (chosen === correct);

        // Apply visual green/red highlighting to show the correct answer
        highlightOptions(chosen, correct);
    }

    // Increment the local score counter if the answer was correct
    // then refresh the score label in the page header
    if (isCorrect) score++;
    document.getElementById('score-lbl').textContent = 'Score: ' + score;

    // Notify the Python backend of the result so it can:
    //   1. Update the session total_correct / total_questions 
    //   2. Adjust the adaptive weight for this specific question
    await eel.submit_answer(isCorrect, currentIndex)();

    // Display the correct/incorrect feedback banner below the question
    showFeedback(isCorrect);

    // Swap the buttons: hide Submit, reveal Next (or See Results on last round)
    document.getElementById('submit-btn').style.display = 'none';
    document.getElementById('next-btn').style.display   = 'inline-block';
}


// ── Option highlighting ──────────────────────────────────────

function highlightOptions(chosen, correct) {
   
    document.querySelectorAll('input[name="ans"]').forEach(function (r) {
        r.disabled = true;
    });

    var chosenLbl  = document.getElementById('opt-' + chosen);
    var correctLbl = document.getElementById('opt-' + correct);

    if (chosenLbl)  chosenLbl.classList.add(chosen === correct ? 'opt-correct' : 'opt-wrong');
    if (correctLbl && chosen !== correct) correctLbl.classList.add('opt-correct');
}


// ── Feedback banner ──────────────────────────────────────────

function showFeedback(isCorrect) {
    // Make the result div visible — it starts hidden inside the card
    var resultDiv = document.getElementById('result');
    resultDiv.style.display = 'block';

    if (isCorrect) {
        resultDiv.textContent = 'Correct! Well done!';
        resultDiv.className   = 'result show correct';
    } else {
        // For fill_blank, read the canonical answer that was stored on the card
        // when the question was rendered — this is the display version only
        var card    = document.querySelector('.card');
        var display = card ? card.dataset.correctDisplay : '';

        if (currentType === 'fill_blank') {
            resultDiv.textContent = 'Wrong! The correct answer was: ' + display;
        } else {
            // For MC, look up the text of the correct option label by its ID
            // so we can show the full option string, not just the index number
            var correct     = parseInt(document.querySelector('.options-group').dataset.correct);
            var correctText = document.getElementById('opt-' + correct);
            resultDiv.textContent = 'Wrong! The correct answer was: ' +
                (correctText ? correctText.textContent.trim() : display);
        }
        resultDiv.className = 'result show incorrect';
    }
}


// ── Navigation ───────────────────────────────────────────────

async function goNext() {
    // Increment the round counter first — currentRound is only ever
    // incremented here, never inside loadQuestion(), so it stays accurate
    currentRound++;

    // Once all rounds are complete, switch to the results screen
    // Otherwise request and render the next question
    if (currentRound >= TOTAL_ROUNDS) {
        await showResults();
    } else {
        await loadQuestion();
    }
}


// ── Results screen ───────────────────────────────────────────

async function showResults() {
  
    document.getElementById('quiz-area').style.display = 'none';


    var allStats = await eel.get_all_stats()();

    // Calculate the overall percentage score for the hero display
    var pct = Math.round((score / TOTAL_ROUNDS) * 100);

    var area = document.getElementById('results-area');
    area.style.display = 'block';

    // Choose a grade label to show alongside the score based on how well they did
    var grade = pct >= 80 ? 'Excellent!' : pct >= 60 ? 'Good job!' : 'Keep practising!';

    // Inject the results layout: a score hero card and a breakdown table structure
    area.innerHTML =
        '<div class="card results-hero">' +
            '<h2>Quiz Complete!</h2>' +
            '<p class="big-score">' + pct + '%</p>' +
            '<p class="grade-label">' + grade + '</p>' +
            '<p>' + score + ' correct out of ' + TOTAL_ROUNDS + '</p>' +
        '</div>' +
        '<div class="card">' +
            '<h3>Question Breakdown</h3>' +
            '<table class="breakdown-table" id="breakdown">' +
                '<thead><tr>' +
                    '<th>Question</th>' +
                    '<th>Type</th>' +
                    '<th>Attempts</th>' +
                    '<th>Correct</th>' +
                    '<th>%</th>' +
                '</tr></thead>' +
                '<tbody id="breakdown-body"></tbody>' +
            '</table>' +
        '</div>' +
        '<button class="submit-btn retry-btn" onclick="retryQuiz()">Try Again</button>';

    //one row per question that was attempted
    var tbody = document.getElementById('breakdown-body');
    for (var idx in allStats) {
        var s = allStats[idx];

        // Colour-code each row based on that question's individual performance
        // Green >= 80%, yellow >= 50%, red below 50%
        var bg      = s.percentage >= 80 ? 'row-good' : s.percentage >= 50 ? 'row-ok' : 'row-bad';
        var typeLbl = s.type === 'fill_blank' ? 'Fill' : 'MC';

        var row = document.createElement('tr');
        row.className = bg;
        row.innerHTML =
            '<td>' + s.question + '</td>' +
            '<td class="type-cell">' + typeLbl + '</td>' +
            '<td class="num-cell">' + s.attempts   + '</td>' +
            '<td class="num-cell">' + s.correct    + '</td>' +
            '<td class="num-cell">' + s.percentage + '%</td>';
        tbody.appendChild(row);
    }
}

async function retryQuiz() {
    // Tell Python to reset all weights and stats back to their starting values
    await eel.reset_quiz()();
    // Reload the page to reset all JavaScript state variables as well

    location.reload();
}