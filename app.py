import eel

#Where my HTML files will be 
eel.init('frontend')
#--------------------------


#-------Where Quiz Data will be handled---------#
total_correct = 0

@eel.expose
def prepare_quiz_data():        
    global total_correct
    total_correct = total_correct + 1 
    print("Total correct answers:", total_correct)
    return(total_correct)
    # Load questions from file
    # Save user info
    



#-----------------------------------------------#



#To start the app 
eel.start('homepage.html', size=(600, 400))
#-----------------------------------------

