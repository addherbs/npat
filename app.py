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

# @app.route ('/eachUser', methods=['GET', 'POST'])
# def eachUser():
#     if request.method == 'post':
#         userNames = firebase.get('/lobby/'+lobby_key+"/"+'users',None)
#         return render_template ('GamePage.html', currentLobby=entireLobbyData, currentUserKey=user_key)


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    # animal = request.form.get('animal')
    # name = request.form.get('name')
    # place = request.form.get('place')
    # thing = request.form.get('thing')

    # currentRound=request.form.get('currentRound')
    # print("currentRound"+currentRound)
    data = {
        'A': 'animal',
        'N': 'name',
        'P': 'place',
        'T': 'thing'
    }
    print(session['user_key'])
    firebase.put('/lobby/-KvNi0Bna6I-F-03Rx9x/rounds/round1/'+session["user_key"],session["user_key"] ,data)
    return '<h1>success</h1>'

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


@app.route("/calculateScores", methods=['GET','POST'])
def calculateScores():

    name = dict()
    place =dict()
    animal = dict()
    thing = dict()
    print("Calc starts")
    lobbyName = "-KvMjQg8AS2PUJUpbqFi"
    currentRound = "round1"
    # dbPath = '/lobby/'+lobbyName+'/'+currentRound+'/'
    dbPath = '/lobby/' + lobbyName + '/'

    lobbyData = firebase.get(dbPath, None)
    # print(dbPath)
    roundsData = lobbyData['rounds']
    # print(roundsData)
    # print (roundsData['round1'])

    for round in roundsData:
        print("Round: "+ str(round))
        allUsers = roundsData[str(round)]
        print(roundsData[str(round)])
        totalScore = dict()
        for eachUser in allUsers:
            print(eachUser)
            if (  not (eachUser in totalScore.keys())):
                print("User"+ eachUser + "entered into the dictionary")
                totalScore[eachUser] = int(0)

            print(allUsers[str(eachUser)])
            print(allUsers[str (eachUser)][str('A')])
            print (allUsers[str (eachUser)][str ('N')])

            a = allUsers[str (eachUser)][str('A')]
            n = allUsers[str (eachUser)][str ('N')]
            p = allUsers[str (eachUser)][str ('P')]
            t = allUsers[str (eachUser)][str ('T')]

            if ( not (a in animal.keys() )):
                print("This animal does not exist")
                animal[a] = eachUser
            else:
                print("This animal does not exist")
                currentValue = animal[a] + "," + eachUser
                animal[a] = currentValue


            if ( not (n in name.keys() )):
                print ("This name does not exist")
                name[n] = eachUser
            else:
                print("This animal does not exist")
                currentValue = name[n] + "," + eachUser
                name[n] = currentValue


            if ( not (p in place.keys() )):
                print ("This place does not exist")
                place[p] = eachUser
            else:
                print("This animal does not exist")
                currentValue = place[p] + "," + eachUser
                place[p] = currentValue


            if ( not (t in thing.keys() )):
                print ("This thing does not exist")
                thing[t] = eachUser
            else:
                print("This animal does not exist")
                currentValue = thing[t] + "," + eachUser
                thing[t] = currentValue

        print ("=====================")
        print(name)
        print (place)
        print (animal)
        print (thing)
        print ("=====================")

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
        for round in roundsData:
            allUsers = roundsData[str (round)]
            for eachUser in allUsers:
                firebase.put('/lobby/' + lobbyName + '/rounds/round1/'+ eachUser,'TP', totalScore[eachUser] )


    print ("Calc ends")
    return ("Hey Man")


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
