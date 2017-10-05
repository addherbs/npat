from flask import Flask, render_template, request, redirect, make_response, session
from firebase import firebase
import random
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'This is rushikesh app lol'

firebase = firebase.FirebaseApplication("https://name-place-animal-thing-b533b.firebaseio.com/", None)

# this route is defined as the route for the main/index page
@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'GET':
        # result = firebase.get ('/users', None)
        # print('Here are all the users')
        # for eachresult in result:
        #     print(eachresult)
        return render_template('server.html')


@app.route('/index', methods=['GET','POST'])
def dashboard():
    this_username = request.form.get('username')
    key_of_object = firebase.post ('/users', {'name': this_username, 'key_of_user': ""})
    key_of_user = key_of_object['name']
    print("Key of this guy is ", key_of_user )
    session['username'] = this_username
    session['user_key'] = key_of_user
    firebase.put('/users/'+key_of_user,'key_of_user',key_of_user)
    print("Firebase user added ", this_username)
    return render_template('dashboard.html', username = this_username)


@app.route('/twoButton', methods=['GET','POST'])
def twoButton():
    operation_keys = request.form.keys ()
    selected_operation = [i for i in operation_keys]
    createLobby = 'createLobby'
    showLobby = 'showLobby'
    if (selected_operation[0] == createLobby):
        return redirect('/createLobby')

    if (selected_operation[0] == showLobby):
        return redirect ('/showLobby')


@app.route('/createLobby', methods=['GET','POST'])
def createLobby():
    if request.method == 'GET':
        return render_template('createLobby.html')

    if request.method == 'POST':
        print("Post call to createLobby")
        lobbyName = request.form.get ('lobbyName')
        number_of_rounds = request.form.get ('numberOfRounds')
        status = False
        number_of_rounds = int(number_of_rounds)
        currentUserKey = session['user_key']
        currentUser = firebase.get ('/users/'+ currentUserKey, None)
        print(currentUser)

        randomNumberList = []
        for num in range(number_of_rounds):
            randomNum = random.randint(0,25)
            randomNumberList.append(
                chr(65+randomNum)
            )

        print("checking starts")
        lobbyKeyName = firebase.post ('/lobby',
                                      {'lobby_name': lobbyName, 'number_of_rounds': number_of_rounds, 'created_by': session['username'],
                                       'running': status, 'users': {
                                          currentUserKey: currentUser
                                      }, 'random_char_list': randomNumberList })

        firebase.put('/lobby/'+lobbyKeyName['name'], 'key_of_lobby', lobbyKeyName['name'])
        # firebase.post('/lobby/'+lobbyKeyName['name'], {'keyOfLobby': lobbyKeyName['name']})
        print(lobbyKeyName['name'])
        print ("checking ends")
        print ("----------------------------")
        return render_template('GamePage.html', lobbyTitle = lobbyName , number_of_rounds = number_of_rounds, owner = session['user_key'])


@app.route ('/showLobby', methods=['GET', 'POST'])
def listOfAllLobies():
    if request.method == 'GET':
        print ("GET call to createLobby")
        # lobbiesList = ['lobby 1', 'Lobby 2']
        lobbyList = []
        get = firebase.get('/lobby', None)
        for mykey in get:
            createdBy = get[mykey]['created_by']
            running=get[mykey]['running']
            key_of_lobby=get[mykey]['key_of_lobby']
            lobby_name=get[mykey]['lobby_name']
            # print (createdBy)
            if running==False:
                data={
                    'created_by': createdBy,
                    'key_of_lobby': key_of_lobby,
                    'lobby_name': lobby_name,
                    'current_user_key': session['user_key']
                }
                # print (data)
                lobbyList.append(data)
            print("-----------------")


        return render_template ('listOfAllLobies.html', lobbiesList=lobbyList)

@app.route("/joinLobby", methods=['GET','POST'])
def joinLobby():
    print ("joinLobby method starts")
    currentLobby = json.loads(request.form["joinLobby"].replace("'", '"'))
    print("joinLobby starts")
    print(currentLobby)

    lobby_key = currentLobby['key_of_lobby']
    user_key = currentLobby['current_user_key']

    currentUser = firebase.get ('/users/' + user_key, None)
    firebase.put ('/lobby/' + lobby_key+ '/users',user_key , currentUser)

    entireLobbyData = firebase.get('/lobby/'+lobby_key, None)

    return render_template('GamePage.html', currentLobby = entireLobbyData, currentUserKey = user_key )

# KvMWOr9zFNAeGrbebu4

@app.route ('/gameOver', methods=['GET', 'POST'])
def gameOver():
    print ("Entered Game Over")
    operation_keys = request.form.keys ()
    selected_operation = [i for i in operation_keys]
    replay = 'replay'
    exitClicked = 'exit'
    if (selected_operation[0] == replay):
        print ("Do Exit Code Here")
        return redirect ('/index')

    if (selected_operation[0] == exitClicked):
        print("Do Exit Code Here")
        return redirect ('/')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    animal = request.form.get('animal')
    name = request.form.get('name')
    place = request.form.get('place')
    thing = request.form.get('thing')

    # currentRound=request.form.get('currentRound')
    # print("currentRound"+currentRound)
    lobbyList = []
    get = firebase.get('/lobby', None)
    for eachkey in get:
        # createdBy = get[eachkey]['created_by']
        key_of_lobby = get[eachkey]['key_of_lobby']
        running = get[eachkey]['running']
        if running == False:
            data = {
                'A': animal,
                'N': name,
                'P': place,
                'T': thing
            }
            # print (data)
            lobbyList.append(data)
            print (lobbyList)
        firebase.post('/lobby/-KvMxBQ2HI2LT_YjZKgk/rounds/round1/'+session["username"], lobbyList)
    return '<h1>success</h1>'
#Causes the app to start
if __name__ == '__main__':
    app.run()
