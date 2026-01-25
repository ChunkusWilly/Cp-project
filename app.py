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

@eel.expose
def prepare_quiz_data(is_correct):        
    global total_correct, total_questions
     
    total_questions = total_questions + 1
    
    if is_correct:
        total_correct = total_correct + 1


    correct_answer_statistic = (total_correct / total_questions) * 100
<<<<<<< HEAD
    correct_answer_statistic = round(correct_answer_statistic, 1)

=======
    correct_stat = round(correct_answer_statistic)
    
>>>>>>> 3e9a89b411cfec7fc942397e2b2a5ef9c399bbcd
    print("Total correct answers:", total_correct)
    print("Total questions:", total_questions)
    print("Percentage correct:", correct_stat)


    return {
        'Total correct': total_correct,
        'Percentage correct': correct_stat
    }
    # Load questions from file
    # Save user info
    



#-----------------------------------------------#
<<<<<<< HEAD
if  __name__ == '__main__':
    eel.start('login.html', size=(800, 600))
=======

>>>>>>> 3e9a89b411cfec7fc942397e2b2a5ef9c399bbcd


#To start the app 
eel.start('homepage.html', size=(600, 400))
#-----------------------------------------

