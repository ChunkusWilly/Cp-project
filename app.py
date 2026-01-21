import eel
import json
import os

#Where my HTML files will be 
eel.init('frontend')
#-------- Sign up and Login System ---------#

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
    
    print("Total correct answers:", total_correct)
    print("Total questions:", total_questions)
    print("Percentage correct:", correct_answer_statistic)


    return {
        'Total correct': total_correct,
        'Percentage correct': correct_answer_statistic
    }
    # Load questions from file
    # Save user info
    



#-----------------------------------------------#
if  __name__ == '__main__':
    eel.start('signup.html', size=(800, 600))


#To start the app 
eel.start('homepage.html', size=(600, 400))
#-----------------------------------------

