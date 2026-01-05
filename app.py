import eel

#Where my HTML files will be 
eel.init('frontend')
#--------------------------


#-------Where Quiz Data will be handled---------#
@eel.expose
def prepare_quiz_data():        
    print("Hello")
    sup = "hello"
    return sup
    # Load questions from file
    # Save user info
  
    return True
#-----------------------------------------------#



#To start the app 
eel.start('homepage.html', size=(600, 400))
#-----------------------------------------

