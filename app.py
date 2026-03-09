import eel
import json
import os
import random

# eel.init must come first, pointing at your frontend folder
eel.init('frontend')

# =============================================
# USER SYSTEM
# =============================================

USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

@eel.expose
def signup(username, email, password):
    try:
        if not username or not email or not password:
            return {'success': False, 'message': 'Fill in all boxes'}
        users = load_users()
        if username in users:
            return {'success': False, 'message': 'Username already exists'}
        users[username] = {'email': email, 'password': password}
        save_users(users)
        return {'success': True, 'message': 'Signup successful!'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

@eel.expose
def login(username, password):
    try:
        if not username or not password:
            return {'success': False, 'message': 'Fill in all boxes'}
        users = load_users()
        if username not in users:
            return {'success': False, 'message': 'Username not found'}
        if users[username]['password'] != password:
            return {'success': False, 'message': 'Incorrect password'}
        return {'success': True, 'message': 'Login successful!', 'email': users[username]['email']}
    except Exception as e:
        return {'success': False, 'message': str(e)}

@eel.expose
def navigate_to_signup():
    eel.show('signup.html')

@eel.expose
def navigate_to_login():
    eel.show('login.html')

@eel.expose
def navigate_to_homepage():
    eel.show('homepage.html')


# =============================================
# QUIZ SYSTEM
# =============================================

MIN_WEIGHT = 0.2
MAX_WEIGHT = 8.0

questions        = []
question_weights = {}
question_stats   = {}
total_correct    = 0
total_questions  = 0


@eel.expose
def load_questions():
    """Load questions from JSON and set up weights"""
    global questions
    print("=== load_questions() called ===")

    try:
        with open('quiz_data.json', 'r') as f:
            data = json.load(f)

        questions = data['questions']

        for i in range(len(questions)):
            question_weights[i] = 1.0
            question_stats[i]   = {'attempts': 0, 'correct': 0}

        print(f"Loaded {len(questions)} questions successfully")
        return questions

    except FileNotFoundError:
        print("ERROR: quiz_data.json not found!")
        return []


@eel.expose
def get_next_question():
    """Pick next question using weighted random selection"""
    if not question_weights:
        print("WARNING: No weights - was load_questions() called?")
        return None

    indices      = list(question_weights.keys())
    weights      = [question_weights[i] for i in indices]
    total_weight = sum(weights)
    rand         = random.random() * total_weight
    cumulative   = 0
    chosen       = indices[0]

    for idx, w in zip(indices, weights):
        cumulative += w
        if rand < cumulative:
            chosen = idx
            break

    q = questions[chosen]
    print(f"Picked Q{chosen}: '{q['question'][:40]}'")
    print(f"Weights: { {i: round(v,2) for i,v in question_weights.items()} }")

    return {
        'index':         chosen,
        'question':      q['question'],
        'options':       q['options'],
        'correctAnswer': q['correctAnswer']
    }


@eel.expose
def submit_answer(is_correct, question_index):
    """Record answer and update weight for that question"""
    global total_correct, total_questions

    total_questions += 1
    if is_correct:
        total_correct += 1

    if question_index in question_stats:
        question_stats[question_index]['attempts'] += 1
        if is_correct:
            question_stats[question_index]['correct'] += 1

    if question_index in question_weights:
        current = question_weights[question_index]
        if is_correct:
            question_weights[question_index] = max(MIN_WEIGHT, current * 0.6)
        else:
            question_weights[question_index] = min(MAX_WEIGHT, current * 1.8)
        print(f"Q{question_index} weight: {current:.2f} -> {question_weights[question_index]:.2f}")

    percentage = round((total_correct / total_questions) * 100, 1)
    return {
        'total_correct':   total_correct,
        'total_questions': total_questions,
        'percentage':      percentage
    }


@eel.expose
def get_all_stats():
    """Return per-question stats for the results screen"""
    result = {}
    for i, stats in question_stats.items():
        if stats['attempts'] == 0:
            continue
        pct = round((stats['correct'] / stats['attempts']) * 100, 1)
        result[i] = {
            'question':   questions[i]['question'] if i < len(questions) else '?',
            'attempts':   stats['attempts'],
            'correct':    stats['correct'],
            'percentage': pct
        }
    return result


@eel.expose
def reset_quiz():
    """Reset all weights and stats"""
    global total_correct, total_questions
    total_correct   = 0
    total_questions = 0
    for key in question_weights:
        question_weights[key] = 1.0
    for key in question_stats:
        question_stats[key] = {'attempts': 0, 'correct': 0}
    print("Quiz reset")


# =============================================
# START APP
# =============================================
if __name__ == '__main__':
    eel.start('login.html', size=(800, 600))