import json
from routes import app, version
from flask import Response, request, jsonify
import sqlite3
import jwt 
import datetime
from functools import wraps

database_locale = 'routes\\kanban.db'


def token_required(f):
    # wrapper function for the jwt authentication
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            conn = sqlite3.connect(database_locale)
            c = conn.cursor()
            c.execute("SELECT userId FROM user WHERE userId = ?", (str(data['user_id'])[1:-1],))
            u_id = c.fetchone()
            conn.commit()
            conn.close()
        except:
            return jsonify({"message" : "Token is Invalid"}), 401

        return f(u_id, *args, **kwargs)
    
    return decorated



def token_generate(username):
    # this is to generate the jwt token
    conn = sqlite3.connect(database_locale)
    c = conn.cursor()
    c.execute("SELECT userId FROM user WHERE userName = ?", (username,))
    u_id = c.fetchone()
    conn.commit()
    conn.close()

    token = jwt.encode({'user_id' : u_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(hours=5)}, app.config['SECRET_KEY'])    
    return token

@app.route(f"{version}/login", methods=["POST"])
def login():
    

    user_profile = ("userId", "firstName", "lastName", "userName", "password","phoneNumber","gmail", "token")
    # getting login info from the form
    login = {
        "userName" : request.form["userName"],
        "password" : request.form["password"]
    }

    # using try catch for sys error and check pass
    try:
        conn = sqlite3.connect(database_locale)
        c = conn.cursor()
        c.execute("SELECT * FROM user WHERE userName = ?", (login["userName"],))
        user_details = c.fetchone()

        if user_details[4] == login["password"]:
            conn.commit()
            conn.close()
            token = token_generate(login["userName"])
            user_details = user_details + (token,)

            if len(user_details) == len(user_profile):
                resultDict = {user_profile[i] : user_details[i] for i, _ in enumerate(user_profile)}            
                return Response(
                                response=json.dumps({"userDetails":resultDict}),
                                status=200,
                                mimetype="application/json")
        else:
            return Response(
                            response=json.dumps({"message" : "Password Incorrect. Try again!!"}),
                            status=401,
                            mimetype="applicatiion/json")

    except sqlite3.Error as e:
        print(e)
        return Response(
                        response=json.dumps({"message" : "ERROR"}),
                        status=401,
                        mimetype="applicatiion/json")
    
    


@app.route(f"{version}/signup", methods=["POST"])
def signup():

    user_profile = ("userId", "firstName", "lastName", "userName", "password","phoneNumber","gmail", "token")
# creating a user dict to store the values from the forms
    user = {"fname" : request.form["firstName"],
            "lname" : request.form["lastName"],
            "gmail" : request.form["gmail"],
            "username" : request.form["userName"],
            "password" : request.form["password"],
            "cpassword" : request.form["cPassword"],
            "phoneNumber" : request.form["phoneNumber"]}

    if user["password"] == user["cpassword"]:
        
        # creating a connection to database and initializing the cursor
        conn = sqlite3.connect(database_locale)
        c = conn.cursor()
        c.execute("INSERT INTO user(firstName, lastName, gmail, userName, password, phoneNumber) VALUES (?, ?, ?, ?, ?, ?)", (user["fname"], user["lname"], user["gmail"], user["username"], user["password"], user["phoneNumber"]))
        conn.commit()
        # note create a function to retrieve the uid and create a token and send it back
        c.execute("SELECT * FROM user WHERE userName = ?",(user["username"],))
        user_details = c.fetchone()    
        token = token_generate(user["username"])
        
        user_details = user_details + (token,)
        if len(user_details) == len(user_profile):
            resultDict = {user_profile[i] : user_details[i] for i, _ in enumerate(user_profile)}
            return Response(
                response=json.dumps({"userDetails": resultDict}),
                status=200,
                mimetype="application/json"
            )
    else:
        return Response(
            response=json.dumps({"message" : "Password Incorrect. Try again!!"}),
            status=401,
            mimetype="applicatiion/json"
        )
