from flask import Flask, render_template, redirect, request, session, jsonify
from cs50 import SQL
from helpers import login_required, dictionary
from werkzeug.security import check_password_hash, generate_password_hash
import random
from django.http import JsonResponse
import time

#DJANGO SETTINGS >>>>> https://docs.djangoproject.com/en/3.1/topics/settings/
from django.conf import settings

settings.configure(DEBUG=True)

#Para ele reconhecer o Django
## >>>>>> https://stackoverflow.com/questions/9462212/import-error-no-module-named-django
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')

app = Flask (__name__)

#NEEDS TO CONFIGURATE different session type and a key
##https://stackoverflow.com/questions/26080872/secret-key-not-set-in-flask-session-using-the-flask-session-extension
app.config['SESSION_TYPE'] = 'filestystem'
app.config['SECRET_KEY'] = 'secret'

#LINK TO  DATABASE
db = SQL('sqlite:///users.db')


@app.route("/")
@login_required
def index():

    # session["user_id"] means get the number that is stored from this current session
    user_id = session["user_id"]

    return render_template("index.html")


@app.route("/login", methods=["GET","POST"])
def login():

    #forget any session
    session.clear()

    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get('username')
    password = request.form.get('password')

    #if user submited something on login page
    if request.method == "POST":

        #if missing username
        if not username:
            return render_template("login.html", text = 'Must type username.') #text is a placeholder for the message

        #if missing password
        elif not password:
            return render_template("login.html", text = 'Must type password.') #text is a placeholder for the message

        #if user typed username and password
        else:
            #check if username matches db (if there is such a user)
            ##Select row that matches that username (selects id, username and password of that user)
            row = db.execute("SELECT * FROM users WHERE username = ?", username)

            print('MY ROW >>>>>', row)

            if not row:
                return render_template("login.html", text = 'Username does not exist.', register_text = 'Register')

            #check if user exists and if password matches
            ##check_password_hash(what you want to compare it to, your input)
            if len(row) != 1 or not check_password_hash(row[0]['password'], password):
                return render_template("login.html", text = 'Invalid username or password')

            #store session's id as the id of current user
            session['user_id'] = row[0]['id']

            #Select current user row in scores
            score_rows = db.execute('SELECT * FROM scores WHERE user_id = ?', session['user_id'])
            #If user hasn't played yet
            if not score_rows:
                #insert row for current user
                db.execute('INSERT INTO scores (user_id, score) VALUES (?, ?)', session['user_id'], 0)

            return redirect('/')

@app.route("/register", methods=["GET", "POST"])
def register():

    #If user got here through clicking a link
    if request.method == 'GET':
        return render_template('register.html')

    #If user got here through submitting something
    if request.method == 'POST':

        #Get username
        username = request.form.get('username')

        #Get password
        password = request.form.get('password')

        #Get confirmation
        conf = request.form.get('conf')


        #if missing username
        if not username:
            return render_template("login.html", text = 'Must type username.') #text is a placeholder for the message

        #if missing password
        elif not password:
            return render_template("login.html", text = 'Must type password.') #text is a placeholder for the message

        #if missing confirmation
        elif not conf:
            return render_template("login.html", text = "Passwords don't match.") #text is a placeholder for the message


    #ID
        user_id = 1
        rows = db.execute('SELECT * FROM users')
        #While the're users with ids that match what I have
        for i in range(len(rows)):
            print(len(rows))
            print('i IS NOW >>>',i)
            #If any id on database matches current id
            if rows[i]['id'] == user_id:
                print("THERE IS A MATCH>>>>", rows[i]['id'])
                #increment 1
                user_id = user_id + 1
                print("USER ID NOW>>>>", user_id)

    #USERNAME

        #Check if username is already taken
        db_username = db.execute('SELECT username FROM users WHERE username = ?', username)
        print(db_username)

        if db_username:
            return render_template('register.html', text = 'Username already taken.')

    #PASSWORD

        #Hash password
        #https://werkzeug.palletsprojects.com/en/1.0.x/utils/
        hash_pass = generate_password_hash(password, method='plain', salt_length=8)

    #CONFIRMATION


        #Hash confirmation
        hash_conf = generate_password_hash(conf, method='plain', salt_length=8)


        #If confirmation and password are different
        if hash_conf != hash_pass:
            return render_template('register.html', text = "Passwords don't match")

    #INSERT INTO TABLE

        #Insert user into table
        db.execute('INSERT INTO users (id, username, password) VALUES (?,?,?)', user_id, username, hash_pass)

        return redirect('/login')

@app.route("/logout")
@login_required
def lougout():
    session.clear()
    return redirect("/login")


@app.route('/player', methods =['POST', 'GET'])
@login_required
def player():
    if request.method == 'GET':


        #Get score of current user
        score = db.execute('SELECT score FROM scores WHERE user_id = ?', session['user_id'])
        print('CURENT SCORE BITCHESSS >>>>', score[0]['score'])

        #Insert score in page render
        return render_template('player.html', score = score[0]['score'])

    if request.method == 'POST':

        print('The word was >>>>>>', data)

        #Get guess
        guess = request.form.get('guess')


        #take the word 'name' out of the list
        for i in range(len(guess) - 1):
            guess[i] = guess[i + 1] #0 becomes 1, 1 becomes 2, 2 becomes 3
        guess = guess[:len(guess) - 1]


        print('GUESS >>>>', guess)

        #Get User id
        userId = session['user_id']

        print('USER ID, MAN!! >>>>', userId)

        #Get current score from user (and id)
        rows = db.execute('SELECT * FROM scores WHERE user_id = ?', userId)

        print('GET THAT CURR SCORE!>>>>', rows)

        #if this user hasn't played yet
        ##add them to the table with a score of 0
        ##select user from table
        if not rows:
            db.execute('INSERT INTO scores (user_id, score) VALUES (?, ?)', userId, 0)
            rows = db.execute('SELECT * FROM scores WHERE user_id = ?', userId)

        #Get score of current user
        points = rows[0]['score']

        print('POINTS>>>>', points)

        print('GUESS LOWER >>>>>', guess.lower())
        print('DATA[WORD] LOWER >>>>>', data['word'].lower())

        #If correct guess, increase points by 1
        if guess.lower() == data['word'].lower():
            print('CORRECT')
            points += 1
            print('YOU GAINED A POINT!')
            #Update score
            db.execute('UPDATE scores SET score = ? WHERE user_id = ?', points, userId )
            print('YEAH!')
            return render_template('results.html', title = 'Correct!', t1 = 'The search was', word = data['word'], t2 = 'Your guess was', guess = guess, score = points)
            #return redirect('/results')
        #If wrong guess
        else:
            print("YOU LOST, BUT THAT'S OK :)")
            return render_template('results.html', title = 'Incorrect...', t1 = 'The search was', word = data['word'], t2 = 'Your guess was', guess = guess, score = points)
            #return redirect('/results')


@app.route('/dic')
@login_required
def dic():

    word = dictionary('dictionaries/nouns.rtf')
    print('DATA >>>>>>', word)
    global data
    data = {'word': word}
    print('Jsonify >>>>>>', jsonify(word))
    return jsonify(word)


@app.route('/multi1', methods =['POST', 'GET'])
@login_required
def multi1():

    #If user got here from link
    if request.method == 'GET':

        #Get score of current user
        score = db.execute('SELECT score FROM scores WHERE user_id = ?', session['user_id'])
        print('CURENT SCORE BITCHESSS >>>>', score[0]['score'])

        #Insert score in page render
        return render_template('multi1.html', score = score[0]['score'])

    #If user inputed something
    if request.method == 'POST':

        session['inp1'] = request.form.get('input1')
        print('THIS >>>>>>', session['inp1'])

        return redirect('/multi2')


@app.route('/ret', methods =['POST', 'GET'])
@login_required
def ret():

    #Get search value
    #return json object (to use in javascript)
    print('SESSION INP1 >>>>>>', session['inp1'])
    word = session['inp1']
    print('INPUT WORD >>>>>>', word)
    #global inp1
    data = {'word': word}
    print('Jsonify >>>>>>', data['word'])
    print('Jsonify >>>>>>', jsonify(data))
    return jsonify(word)


@app.route('/multi2', methods =['POST', 'GET'])
@login_required
def multi2():

    #If user got here from link
    if request.method == 'GET':

        #Get score of current user
        score = db.execute('SELECT score FROM scores WHERE user_id = ?', session['user_id'])
        print('CURENT SCORE BITCHESSS >>>>', score[0]['score'])

        #Insert score in page render
        return render_template('multi2.html', score = score[0]['score'])

    #If user inputed something
    if request.method == 'POST':

        print('ThE wORd wAS', session['inp1'])

        #Get guess
        # guess = request.form.get('input2')
        session['guess'] = request.form.get('input2')

        #take the ' ' out of session['inp1']
        for i in range(len(session['inp1']) - 1):
            session['inp1'][i] = session['inp1'][i + 1] #0 becomes 1, 1 becomes 2, 2 becomes 3
        session['inp1'] = session['inp1'][:len(session['inp1']) - 1]

        #take the ' ' out of guess
        for i in range(len(session['guess']) - 1):
            session['guess'][i] = session['guess'][i + 1] #0 becomes 1, 1 becomes 2, 2 becomes 3
        session['guess'] = session['guess'][:len(session['guess']) - 1]

        print('GUESS >>>>', session['guess'])

        #Get User id
        userId = session['user_id']

        print('USER ID, MAN!! >>>>', userId)

        #Get current score from user (and id)
        rows = db.execute('SELECT * FROM scores WHERE user_id = ?', userId)

        print('GET THAT CURR SCORE!>>>>', rows)

        #if this user hasn't played yet
        ##add them to the table with a score of 0
        ##select user from table
        if not rows:
            db.execute('INSERT INTO scores (user_id, score) VALUES (?, ?)', userId, 0)
            rows = db.execute('SELECT * FROM scores WHERE user_id = ?', userId)

        #Get score of current user
        points = rows[0]['score']

        print('POINTS>>>>', points)

        #If correct guess, increase points by 1
        if session['inp1'].lower() == session['guess'].lower():
            print('CORRECT')
            points += 1
            print('YOU GAINED A POINT!')
            #Update score
            db.execute('UPDATE scores SET score = ? WHERE user_id = ?', points, userId )
            print('YEAH!')
            #copy to another variable
            w = session['inp1']
            g = session['guess']
            s = points
            return render_template('results.html', title = 'Correct!', t1 = 'The search was', word = w, t2 = 'Your guess was', guess = g, score = s)
        #If wrong guess
        else:
            print("YOU LOST, BUT THAT'S OK :)")
            w = session['inp1']
            g = session['guess']
            s = points
            # del inp
            # del guess
            return render_template('results.html', title = 'Incorrect...', t1 = 'The search was', word = w, t2 = 'Your guess was', guess = g, score = s)