import eel
import json
import os
import random


eel.init('frontend')

# =============================================
# USER SYSTEM
# =============================================

# Path to the JSON file that stores all registered user accounts
USERS_FILE = 'users.json'

def load_users():
    # Check whether the users file exists on disk before trying to open it
    # If it doesn't exist yet, return an empty dictionary as a safe default
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
   
  
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

@eel.expose
def signup(username, email, password):
    # @eel.expose makes this Python function callable directly from JavaScript via eel
    try:
        # All three fields must be filled in before we proceed with registration
        if not username or not email or not password:
            return {'success': False, 'message': 'Fill in all boxes'}
        users = load_users()
        # Prevent duplicate accounts — each username must be unique across all users
        if username in users:
            return {'success': False, 'message': 'Username already exists'}
        # Store the new user entry and immediately persist it to disk
        users[username] = {'email': email, 'password': password}
        save_users(users)
        return {'success': True, 'message': 'Signup successful!'}
    except Exception as e:
        # Catch any unexpected errors and return them as a readable message
        return {'success': False, 'message': str(e)}

@eel.expose
def login(username, password):
    try:
        # Both fields must be present before we attempt any lookup
        if not username or not password:
            return {'success': False, 'message': 'Fill in all boxes'}
        users = load_users()
        # First verify that the username exists in the registered accounts
        if username not in users:
            return {'success': False, 'message': 'Username not found'}
        # Then check the supplied password matches the one stored at signup
        if users[username]['password'] != password:
            return {'success': False, 'message': 'Incorrect password'}
        # Return the email alongside the success flag so the frontend can
        # use it to personalise any welcome messages
        return {'success': True, 'message': 'Login successful!', 'email': users[username]['email']}
    except Exception as e:
        return {'success': False, 'message': str(e)}

@eel.expose
def navigate_to_signup():
    # Tell eel to swap the currently displayed HTML page to the signup screen
    eel.show('signup.html')

@eel.expose
def navigate_to_login():
    # Navigate the user back to the login page (e.g. when coming from signup)
    eel.show('login.html')

@eel.expose
def navigate_to_homepage():
    # Navigate to the main homepage after a successful login
    eel.show('homepage.html')


# =============================================
# QUIZ SYSTEM
# =============================================

# Lower bound for adaptive weights — a question will never drop below this
# even if it is answered correctly many times in a row
MIN_WEIGHT = 0.2

# Upper bound for adaptive weights — a question will never exceed this
# even if it is answered incorrectly many times in a row
MAX_WEIGHT = 8.0

# Full list of question objects loaded from quiz_data.json
# Initialised as an empty list — populated by load_questions()
questions        = []

# Maps each question's list index to its current probability weight
# Higher weight = more likely to be selected by get_next_question()
question_weights = {}

# Maps each question's list index to a dict tracking attempts and correct count
# Used to generate the per-question breakdown on the results screen
question_stats   = {}

# Session-level running totals used to calculate the overall score percentage
total_correct    = 0
total_questions  = 0


@eel.expose
def load_questions():

    global questions
    print("=== load_questions() called ===")

    try:
        # Open and parse the quiz data JSON file from the project root
        with open('quiz_data.json', 'r') as f:
            data = json.load(f)

        # Store the full question list in the module-level variable
        # so all other functions can reference it throughout the session
        questions = data['questions']

        # Give every question an equal starting weight of 1.0 so that
        # on the first round all questions have the same chance of appearing
        # Also create blank stats entries ready to track attempts and scores
        for i in range(len(questions)):
            question_weights[i] = 1.0
            question_stats[i]   = {'attempts': 0, 'correct': 0}

        print(f"Loaded {len(questions)} questions successfully")

        # Build a sanitised list to return to the JavaScript frontend
        # This removes acceptedAnswers from fill_blank entries so that
        # the answer list is never visible in the browser's network traffic
        safe = []
        for q in questions:
            entry = {
                'type':     q.get('type', 'multiple_choice'),
                'question': q['question'],
            }
            if entry['type'] == 'multiple_choice':
                # Multiple choice questions need their options and correct index
                entry['options']       = q['options']
                entry['correctAnswer'] = q['correctAnswer']
            else:
                # Fill-blank questions only send the canonical display answer
                # so the frontend can show it in the "wrong — correct was X" message
                # The full acceptedAnswers list stays server-side only
                entry['correctAnswer'] = q['correctAnswer']
            safe.append(entry)

        return safe

    except FileNotFoundError:
        # If the data file is missing, log a clear error and return empty
        # so the frontend can display a helpful message rather than crashing
        print("ERROR: quiz_data.json not found!")
        return []


@eel.expose
def get_next_question():
 
    # if the weights table is empty it means load_questions()
    # was never called or failed, so we cannot proceed
    if not question_weights:
        print("WARNING: No weights - was load_questions() called?")
        return None

    # Build parallel lists so we can walk them together during selection
    indices      = list(question_weights.keys())
    weights      = [question_weights[i] for i in indices]
    total_weight = sum(weights)

    # Pick a random point along the combined weight range, then walk through
    # the cumulative sum until we find which question's range it falls into
    # This gives each question a selection probability proportional to its weight
    rand       = random.random() * total_weight
    cumulative = 0
    chosen     = indices[0]   # fallback to first question if loop somehow exhausts

    for idx, w in zip(indices, weights):
        cumulative += w
        if rand < cumulative:
            chosen = idx
            break

    q = questions[chosen]
    print(f"Picked Q{chosen} ({q.get('type', 'mc')}): '{q['question'][:40]}'")
    print(f"Weights: { {i: round(v, 2) for i, v in question_weights.items()} }")

    # Build the response object with only the data the frontend needs
    result = {
        'index':    chosen,
        'type':     q.get('type', 'multiple_choice'),
        'question': q['question'],
    }

    if result['type'] == 'multiple_choice':
        # Send the full options list and the correct answer index for MC questions
        result['options']       = q['options']
        result['correctAnswer'] = q['correctAnswer']
    else:
        # For fill_blank, only send the canonical display answer
        # Actual validation is handled server-side by check_fill_blank_answer()
        # so the acceptedAnswers list is never sent to the browser
        result['correctAnswer'] = q['correctAnswer']

    return result


@eel.expose
def check_fill_blank_answer(question_index, user_answer):

    
    # Bounds check — reject any index that falls outside the loaded questions
    if question_index >= len(questions):
        return False

    q = questions[question_index]

    # Build a normalised list of every accepted answer variant
    # If the question has no acceptedAnswers field, fall back to just correctAnswer
    accepted = [a.lower().strip() for a in q.get('acceptedAnswers', [q['correctAnswer']])]

    # Normalise the user's input in exactly the same way before comparing
    # This ensures "CTRL", "Ctrl", and "ctrl" are all treated as equivalent
    return user_answer.lower().strip() in accepted


@eel.expose
def submit_answer(is_correct, question_index):

    global total_correct, total_questions

    # Increment the session-level counters regardless of correctness
    total_questions += 1
    if is_correct:
        total_correct += 1

    # Update the per-question attempt and correct counters
    if question_index in question_stats:
        question_stats[question_index]['attempts'] += 1
        if is_correct:
            question_stats[question_index]['correct'] += 1

    # Adaptive weight adjustment — the core of the spaced-repetition system:
    # Correct answer -> multiply weight by 0.6 (reduces future appearance frequency)
    # Wrong answer   -> multiply weight by 1.8 (increases future appearance frequency)
    # Both are clamped to the MIN/MAX bounds so weights never become extreme
    if question_index in question_weights:
        current = question_weights[question_index]
        if is_correct:
            question_weights[question_index] = max(MIN_WEIGHT, current * 0.6)
        else:
            question_weights[question_index] = min(MAX_WEIGHT, current * 1.8)
        print(f"Q{question_index} weight: {current:.2f} -> {question_weights[question_index]:.2f}")

    # Calculate the running score percentage to one decimal place
    percentage = round((total_correct / total_questions) * 100, 1)

    return {
        'total_correct':   total_correct,
        'total_questions': total_questions,
        'percentage':      percentage
    }


@eel.expose
def get_all_stats():
 
    result = {}
    for i, stats in question_stats.items():
        # Skip questions that were never shown during this session
        if stats['attempts'] == 0:
            continue

        # Calculate the individual question's success rate from its own counters
            
        pct = round((stats['correct'] / stats['attempts']) * 100, 1)

        result[i] = {
            'question':   questions[i]['question'] if i < len(questions) else '?',
            'type':       questions[i].get('type', 'multiple_choice'),
            'attempts':   stats['attempts'],
            'correct':    stats['correct'],
            'percentage': pct
        }
    return result


@eel.expose
def reset_quiz():
  
    global total_correct, total_questions

    # Zero out the session score counters
    total_correct   = 0
    total_questions = 0

    # Return every question's weight to the neutral starting value of 1.0
    # so all questions have equal probability again at the start of the new attempt
    for key in question_weights:
        question_weights[key] = 1.0

    # Clear every question's recorded attempt and correct answer counts
    for key in question_stats:
        question_stats[key] = {'attempts': 0, 'correct': 0}

    print("Quiz reset")


# =============================================
# START APP
# =============================================
if __name__ == '__main__':
    # Launch the eel desktop window at 800x600, opening on the login page
    eel.start('login.html', size=(800, 600))