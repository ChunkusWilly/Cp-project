import eel

#Where my HTML files will be 
eel.init('frontend')
#--------------------------


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



#To start the app 
eel.start('homepage.html', size=(600, 400))
#-----------------------------------------

