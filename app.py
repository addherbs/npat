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


@app.route ('/showLobby', methods=['GET', 'POST'])
def listOfAllLobies():
    # if request.method == 'POST':
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
                                       'running': status, 'created_by_key': session['user_key'] ,'users': {
                                          currentUserKey: currentUser
                                      }, 'random_char_list': randomNumberList })

        firebase.put('/lobby/'+lobbyKeyName['name'], 'key_of_lobby', lobbyKeyName['name'])

        sendingData = {
            'created_by': session['username'],
            'created_by_key': session['user_key'],
            'key_of_lobby': lobbyKeyName['name'],
            'lobby_name' : lobbyName,
            'number_of_rounds': number_of_rounds,
            'random_char_list': randomNumberList,
            'current_user_key' : session['user_key']
        }

        sendingData = json.dumps(sendingData)

        users = firebase.get('/lobby/'+ lobbyKeyName['name'] + '/users/', None)
        print(users)


        # sendingData = json.dump (sendingData)
        users =  json.dumps(users)

        print(sendingData)
        print (users)


        return render_template('GamePage.html', lobbyJoinDetails = sendingData, listOfAllUsers = users )

@app.route("/userList", methods=['GET','POST'])
def userList():

    inputData = dict(request.form)
    myData = ''
    for key in inputData:
        myData = key

    myData = json.loads(myData)
    lobbyKey = myData['lobbyKey']

    users = firebase.get('/lobby/'+ lobbyKey + '/users/', None)
    print(users)
    users = json.dumps (users)

    return users


@app.route("/joinLobby", methods=['GET','POST'])
def joinLobby():
    # print ("joinLobby method starts")
    currentLobby = json.loads(request.form["joinLobby"].replace("'", '"'))
    # print("joinLobby starts")
    print(currentLobby)

    lobby_key = currentLobby['key_of_lobby']
    user_key = currentLobby['current_user_key']

    currentUser = firebase.get ('/users/' + user_key, None)
    firebase.put ('/lobby/' + lobby_key+ '/users',user_key , currentUser)

    entireLobbyData = firebase.get('/lobby/'+lobby_key, None)

    # print ("=========EntireLobbyData============")
    # print(entireLobbyData)

    sendingData = {
        'created_by': entireLobbyData['created_by'],
        'created_by_key': entireLobbyData['created_by_key'],
        'key_of_lobby': entireLobbyData['key_of_lobby'],
        'lobby_name': entireLobbyData['lobby_name'],
        'number_of_rounds': entireLobbyData['number_of_rounds'],
        'random_char_list': entireLobbyData['random_char_list'],
        'current_user_key': session['user_key']
    }
    # print ("=========Sending Data============")
    # print(sendingData)

    users = firebase.get ('/lobby/' + entireLobbyData['key_of_lobby'] + '/users/', None)
    # print ("=========Users============")
    # print (users)

    sendingData = json.dumps (sendingData)
    users = json.dumps (users)

    return render_template ('GamePage.html', lobbyJoinDetails=sendingData, listOfAllUsers=users)



@app.route('/submit', methods=['GET', 'POST'])
def submit():

    animal = request.form.get('animal')
    name = request.form.get('name')
    place = request.form.get('place')
    thing = request.form.get('thing')
    roundNumber = request.form.get('roundno')
    lobbyKey = request.form.get('lobbykey')
    userKey = request.form.get('userid')


    #
    # animal = 'animal'
    # name = 'Name'
    # place = 'place'
    # thing = 'Thing'
    #
    # roundNumber = "round1"
    # lobbyKey = "-KvfVmzDy6ezik9jKYRM"
    # userKey = "-KvfVtQe4CbAy17RbTW-"

    data = {
        'Animal': animal,
        'Name': name,
        'Place': place,
        'Thing': thing
    }
    insertLocation = '/lobby/' + lobbyKey + '/rounds/' + roundNumber + '/'
    # firebase.put ('/lobby/' + lobby_key + '/users', user_key, currentUser)
    firebase.put (insertLocation, userKey, data)

    result = calculationBeforeGoingBack(lobbyKey, roundNumber)


    return '<h1>success</h1>'

def calculationBeforeGoingBack(lobbyKey, roundNumber):
    lobbyKey = "-KvfVmzDy6ezik9jKYRM"
    currentRound = "round1"
    # Check if all the users have submitted the scores or no
    #     if submitted:
    #         update the 'all_user_submitted' key to true

     if(check_all_users_submitted_for_the_current_round(lobbyKey,currentRound)):


        dbPath = '/lobby/' + lobbyKey + '/'
        firebase.put(dbPath , 'all_user_submitted', True )
        calculateScores(currentRound, lobbyKey)

        # Change the all_user_submitted variable to True


    # Check for 'all_user_submitted' variable in the lobby class
    return "lol"

def checkFlag(lobbyKey):
    # lobbyKey = "-KvfVmzDy6ezik9jKYRM"
    dbPath= '/lobby/' + lobbyKey + '/all_user_submitted'
    print(dbPath)
    result = firebase.get(dbPath, None)
    print(result)
    return result


def check_all_users_submitted_for_the_current_round(lobbyKey, currentRound):

    # lobbyKey = "-KvfVmzDy6ezik9jKYRM"
    # currentRound = "round1"

    dbPathForRoundUsers = '/lobby/' + lobbyKey+ '/rounds/' + currentRound + "/"
    totalUsersInLobby = firebase.get (dbPathForRoundUsers, None)

    dbPathForTotalUsers = '/lobby/' + lobbyKey + '/users/'
    totalUsersSubmitted = firebase.get (dbPathForTotalUsers, None)

    return True if ( len(totalUsersInLobby )== len(totalUsersSubmitted)) else False



# @app.route("/calculateScores", methods=['GET','POST'])
def calculateScores(rNo, lobbyName):

    print ("Calc starts")

    name = dict()
    place =dict()
    animal = dict()
    thing = dict()

    # rNo = "1"
    # lobbyName = "-KvfVmzDy6ezik9jKYRM"

    roundNumber = "round" + rNo

    dbPath = '/lobby/' + lobbyName + '/rounds/' + roundNumber + "/"
    roundData = firebase.get(dbPath, None)

    print(roundData)
    # allUsers = roundData[str(roundNumber)]
    totalScore = dict()
    for eachUser in roundData:
        print(eachUser)
        if (  not (eachUser in totalScore.keys())):
            print("User "+ eachUser + " entered into the dictionary")
            totalScore[eachUser] = int(0)

        # print(roundData[str(eachUser)])
        # print(roundData[str (eachUser)][str('Animal')])
        # print (roundData[str (eachUser)][str ('Name')])

        a = roundData[str (eachUser)][str('Animal')]
        n = roundData[str (eachUser)][str ('Name')]
        p = roundData[str (eachUser)][str ('Place')]
        t = roundData[str (eachUser)][str ('Thing')]

        if ( not (a in animal.keys() )):
            print("This animal does not exist")
            animal[a] = eachUser
        else:
            print("This animal already exist")
            currentValue = animal[a] + "," + eachUser
            animal[a] = currentValue


        if ( not (n in name.keys() )):
            print ("This name does not exist")
            name[n] = eachUser
        else:
            print("This name already exist")
            currentValue = name[n] + "," + eachUser
            name[n] = currentValue


        if ( not (p in place.keys() )):
            print ("This place does not exist")
            place[p] = eachUser
        else:
            print("This place already exist")
            currentValue = place[p] + "," + eachUser
            place[p] = currentValue


        if ( not (t in thing.keys() )):
            print ("This thing does not exist")
            thing[t] = eachUser
        else:
            print("This thing already exist")
            currentValue = thing[t] + "," + eachUser
            thing[t] = currentValue

    # print ("=====================")
    # print(name)
    # print (place)
    # print (animal)
    # print (thing)
    # print ("=====================")

    print ("Validation starts")
    for k,v in name.items():
        print(k , " : ", v)
        if ("," in v):
            splitString = v.split(",")
            for everyUser in splitString:
                print(everyUser)
                totalScore[everyUser] = totalScore[everyUser] + int(5)
        else:
            totalScore[v] = totalScore[v]  + int(10)

    for k,v in place.items():
        print(k , " : ", v)
        if ("," in v):
            splitString = v.split(",")
            for everyUser in splitString:
                print(everyUser)
                totalScore[everyUser] = totalScore[everyUser] + int(5)
        else:
            totalScore[v] = totalScore[v]  + int(10)

    for k,v in animal.items():
        print(k , " : ", v)
        if ("," in v):
            splitString = v.split(",")
            for everyUser in splitString:
                print(everyUser)
                totalScore[everyUser] = totalScore[everyUser] + int(5)
        else:
            totalScore[v] = totalScore[v]  + int(10)

    for k, v in thing.items ():
        print (k, " : ", v)
        if ("," in v):
            splitString = v.split (",")
            for everyUser in splitString:
                print (everyUser)
                totalScore[everyUser] = totalScore[everyUser] + int(5)
        else:
            totalScore[v] = totalScore[v] + int(10)


    print ("Validation ends")
    print(totalScore)

    # for eachCheckUser in
    for eachUser in roundData:
        print(eachUser)
        firebase.put('/lobby/' + lobbyName + '/rounds/round1/'+ eachUser,'TotalScore', totalScore[eachUser] )

    print ("Calc ends")
    return "Hey Man"


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


#Causes the app to start
if __name__ == '__main__':
    app.run()
