from flask import Flask, request, session, render_template, redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = os.getenv("DB_PASSWORD")
app.config["MYSQL_DB"] = "my_web_login"
app.secret_key = os.getenv("SECRET_KEY")

mysql = MySQL(app)


@app.route("/")
def home():
    if "loggedin" in session and session["loggedin"]:
        return render_template("index.html", msg="Welcome " + session["username"])
    else:
        return redirect("login")


@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM accounts WHERE username = %s AND password = %s",
            (username, password),
        )
        account = cursor.fetchone()
        if account:
            session["loggedin"] = True
            session["acc_id"] = account["acc_id"]
            session["username"] = account["username"]
            return render_template("index.html", msg="Welcome " + session["username"])
        else:
            msg = "Incorrect Credentials"
    return render_template("login.html", msg=msg)


@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("acc_id", None)
    session.pop("username", None)
    session.clear()

    return redirect("login")


@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
        and "email" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM accounts WHERE username = %s AND password = %s",
            (username, password),
        )
        account = cursor.fetchone()
        if account:
            msg = "Account already exists!"
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, email, password))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect('/')
    return render_template('register.html', msg = msg)



if __name__ == "__main__":
    app.run(debug=True)
