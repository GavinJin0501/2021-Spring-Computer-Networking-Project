from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_socketio import SocketIO, send
import json
import check_db


GROUPS = {}                    # { group_id/group_name: [members] }
CLIENT_NAME_TO_ID = {}         # { username: socketio_id }

app = Flask(__name__)
app.config["SERECT_KEY"] = "GavinAndAlan"
app.secret_key = "my secret key"
socket = SocketIO(app, cors_allowed_origins='*')


# 1. initial page
@app.route("/")
def initial():
    return render_template("index.html")


# 2.1 login page
@app.route('/login')
def login():
    return render_template('login.html')


# 2.2 login authorize
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        table = check_db.load_table()

        if username not in table or table[username] != password:
            error = 'Invalid login or username'
            return render_template('login.html', error=error)
        else:
            session["Username"] = username
            return redirect(url_for('home'))
    else:
        if "Username" in session:
            return redirect(url_for('home'))
        return render_template("login.html")


# 3.1 register page
@app.route('/register')
def register():
    return render_template('register.html')


# 3.2 register authorize
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']

    # open JSON file to check
    table = check_db.load_table()

    if username in table:
        # If user exists
        error = "This username already exists"
        return render_template('register.html', error=error)
    elif len(password) < 4:
        error = "Password length must be at least 4 characters"
        return render_template('register.html', error=error)
    else:
        table[username] = password
        check_db.write_table(table)
        flash("You are logged in")
        session["Username"] = username
        return redirect(url_for("home"))


# 4. home page
@app.route('/home', endpoint='home')
def home():
    if "Username" in session:
        username = session["Username"]
        # print("Test session:", username)
        post = "Hello Hello"
        return render_template('home.html', username=username, post=post)
    else:
        flash("Don't cheat! Login first!")
        return redirect(url_for("initial"))


@socket.on("message")
def handle_message(msg):
    msg = json.loads(msg)

    # Type 1: Socket, when client connecting to the server, but not authorized
    if msg["Type"] == "Socket":
        user_id = msg["Id"]
        username = msg["Username"]
        CLIENT_NAME_TO_ID[username] = user_id
        print("User '%s':'%s' has connected to the server." % (user_id, msg["Username"]))
        print(CLIENT_NAME_TO_ID)
        # send(msg, broadcast=True)

    elif msg["Type"] == "Post":
        pass


@app.route('/logout')
def logout():
    session.pop('Username', None)
    return redirect('/')


if __name__ == "__main__":
    socket.run(app, debug=True)