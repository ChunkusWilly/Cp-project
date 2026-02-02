import eel
import json
import os

#Where my HTML files will be 
eel.init('frontend')
#-------- Sign up System ---------#

USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

@eel.expose
def signup(username, email, password):
    try:
        # validation checking
        if not username or not email or not password:
            return {'success': False, 'message': 'Fill in all boxes'}
        
        # load existing users
        users = load_users()
        
        # Check if username already exists
        if username in users:
            return {'success': False, 'message': 'Username already exists'}
        
        # Create new user
        users[username] = {
            'email': email,
            'password': password
        }
        
        # Save to file
        save_users(users)
        
        return {'success': True, 'message': 'Signup successful!'}
    except Exception as e:
        return {'success': False, 'message': str(e)}
   
    

def save_users(users):
    #save users to JSON file
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

#-------- Log in System ---------#

@eel.expose
def login(username, password):
    try:
        # Validation checking
        if not username or not password:
            return {'success': False, 'message': 'Fill in all boxes'}
        
        # Load existing users
        users = load_users()
        
        # Check if username exists
        if username not in users:
            return {'success': False, 'message': 'Username not found'}
        
        # Check if password matches
        if users[username]['password'] != password:
            return {'success': False, 'message': 'Incorrect password'}
        
        # Login successful
        return {
            'success': True, 
            'message': 'Login successful!',
            'email': users[username]['email']
        }
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











#-------Where Quiz Data will be handled---------#
total_correct = 0
total_questions = 0 
question_statistics = {}

@eel.expose
def prepare_quiz_data(is_correct, question_index=None):        
    global total_correct, total_questions, question_statistics
     
    total_questions = total_questions + 1
    
    if is_correct:
        total_correct = total_correct + 1
    
    # Track statistics for specific question
    if question_index is not None:
        if question_index not in question_statistics:
            question_statistics[question_index] = {
                'attempts': 0,
                'correct': 0
            }
        
        question_statistics[question_index]['attempts'] += 1
        if is_correct:
            question_statistics[question_index]['correct'] += 1

    correct_answer_statistic = (total_correct / total_questions) * 100
    correct_answer_statistic = round(correct_answer_statistic, 1)

    print("Total correct answers:", total_correct)
    print("Total questions:", total_questions)
    print("Percentage correct:", correct_answer_statistic)
    
    # Print individual question stats if available
    if question_index is not None:
        print(f"Question {question_index} - Attempts: {question_statistics[question_index]['attempts']}, Correct: {question_statistics[question_index]['correct']}")

    return {
        'Total correct': total_correct,
        'Percentage correct': correct_answer_statistic
    }
    # Load questions from file
    # Save user info

#-------Get statistics for a specific question---------#
@eel.expose
def get_question_stats(question_index):
    
    if question_index in question_statistics:
        stats = question_statistics[question_index]
        percentage = (stats['correct'] / stats['attempts']) * 100 if stats['attempts'] > 0 else 0
        return {
            'attempts': stats['attempts'],
            'correct': stats['correct'],
            'percentage': round(percentage, 1)
        }
    return {
        'attempts': 0,
        'correct': 0,
        'percentage': 0
    }
#----------------------------------------------------------#


#-------Get all question statistics------------------------#
@eel.expose
def get_all_question_stats():
    """Get statistics for all questions"""
    all_stats = {}
    for index, stats in question_statistics.items():
        percentage = (stats['correct'] / stats['attempts']) * 100 if stats['attempts'] > 0 else 0
        all_stats[index] = {
            'attempts': stats['attempts'],
            'correct': stats['correct'],
            'percentage': round(percentage, 1)
        }
    return all_stats

#----------------------------------------------------------#
#-------Adding Questions to JSON file---------#
@eel.expose
def add_question(question, options, correct_answer):

    try:
        with open('quiz_data.json', 'r') as file:
            data = json.load(file)
        
        new_question = {
            "question": question,
            "options": options,
            "correctAnswer": correct_answer
        }
        
        data['questions'].append(new_question)
        
        with open('quiz_data.json', 'w') as file:
            json.dump(data, file, indent=2)
        
        return True
    except Exception as e:
        print(f"Error adding question: {e}")
        return False
#-------Loading Questions from JSON file---------#
@eel.expose
def load_questions():
    try:
        with open('quiz_data.json', 'r') as file:
            data = json.load(file)
            return data['questions']
    except FileNotFoundError:
        return []

#-------Starting the App---------

if  __name__ == '__main__':
    eel.start('login.html', size=(800, 600))

#-----------------------------------------------#
