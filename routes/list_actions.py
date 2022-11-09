import mimetypes
from routes import app, version
import json
from flask import Response, request, jsonify
import sqlite3
from routes.user_action import token_required, database_locale

@app.route(f"{version}/createlist", methods=["POST"])
@token_required
def createlist(u_id):
    # getting list details from the form

    list_detatils = {
        "name" : request.form["listName"],
        "description" : request.form["listDescription"],
        "image" : request.form["imageName"]
    }

    try:
        # creating database connection and cursor
        conn = sqlite3.connect(database_locale)
        c = conn.cursor()
        c.execute("INSERT INTO list(listName, listDescription, imageName) VALUES (?, ?, ?)", (list_detatils["name"], list_detatils["description"], list_detatils["image"]))
        c.execute("SELECT listId FROM list WHERE listName=?", (list_detatils["name"],))
        list_id = c.fetchone()
        c.execute("INSERT INTO creates(userId, listId) VALUES(?,?)",(u_id[0],list_id[0]))
        conn.commit()
        conn.close()

        return Response(
            response=json.dumps({"message":f"{list_detatils['name']} list is created"}),
            status=200,
            mimetype="application/json"
        )
    except sqlite3.Error as e:
        print(e)
        return Response(
                        response=json.dumps({"message" : "Cannot create list"}),
                        status=401,
                        mimetype="applicatiion/json")


@app.route(f"{version}/updatelisttitle/<listId>", methods=["POST"])
@token_required
def updatelisttitle(u_id, listId):
    # getting list details from the form

    list_details =  {
        "listName" : request.form["listName"],
        "listDescription" : request.form["listDescription"],
        "imageName" : request.form["imageName"]
    }

    try:
        # creating database connection and cursor
        conn = sqlite3.connect(database_locale)
        c = conn.cursor()
        c.execute("SELECT userId FROM creates WHERE listId=?",(listId,))
        userId = c.fetchone()

        if userId == u_id:
            c.execute("UPDATE list SET listName = ?, listDescription = ?, imageName = ? WHERE listId = ?", (list_details["listName"], list_details["listDescription"], list_details["imageName"], listId))
        else:
            return Response(
                response=json.dumps({"message": "Unauthorized access"}),
                status=200,
                mimetype="application/json"
            )
        conn.commit()
        conn.close()

        return Response(
            response=json.dumps({"message":f" Title is changed to{list_details['listName']}"}),
            status=200,
            mimetype="application/json"
        )
    except sqlite3.Error as e:
        print(e)
        return Response(
                        response=json.dumps({"message" : "Cannot change list title"}),
                        status=401,
                        mimetype="applicatiion/json")


@app.route(f"{version}/getAllList", methods=["GET"])
@token_required
def getAllList(u_id):
    try:

        conn = sqlite3.connect(database_locale)
        c = conn.cursor()
        c.execute("select * from list where listId in (select c.listId from list l, creates c where l.listId = c.listId and c.userId = ?)", (u_id[0],))
        lists = c.fetchall()
        conn.commit()
        conn.close()
        return Response(
            response=json.dumps({"message": f"{lists}"}),
            status=200,
            mimetype="application/json"
        )
    except:
        return Response(
            response=json.dumps({"message":"Cannot display all list"}),
            status=200,
            mimetype="application/json"
        )


@app.route(f"{version}/getList/<listId>", methods=["GET"])
@token_required
def getList(u_id, listId):
    try:
        conn = sqlite3.connect(database_locale)
        c = conn.cursor()
        c.execute("SELECT userId FROM creates WHERE listId=?",(listId,))
        userId = c.fetchone()

        if userId == u_id:
            c.execute("SELECT * FROM list WHERE listId = ?",(listId,))
            List = c.fetchone()
        else:
            return Response(
                response=json.dumps({"message": "Unauthorized access"}),
                status=200,
                mimetype="application/json"
            )

        conn.commit()
        conn.close()

        return Response(
            response=json.dumps({"message": f"{List}"}),
            status=200,
            mimetype="application/json"
        )
        
    except sqlite3.Error as e:
        print(e)
        return Response(
                        response=json.dumps({"message" : "Cannot Display list"}),
                        status=401,
                        mimetype="applicatiion/json")

@app.route(f"{version}/deleteList/<listId>", methods=["POST"])
@token_required
def deleteList(u_id, listId):
    try:
        conn = sqlite3.connect(database_locale)
        c = conn.cursor()
        c.execute("SELECT userId FROM creates WHERE listId=?",(listId,))
        userId = c.fetchone()

        if userId == u_id:
            c.execute("SELECT listName FROM list WHERE listId = ?",(listId,))
            List = c.fetchone()
            c.execute("DELETE FROM LIST WHERE listId = ?",(listId,))
            c.execute("DELETE FROM CREATES WHERE listId = ?",(listId,))
        else:
            return Response(
                response=json.dumps({"message": "Unauthorized access"}),
                status=200,
                mimetype="application/json"
            )

        conn.commit()
        conn.close()

        return Response(
            response=json.dumps({"message": f"{List[0]} is deleted"}),
            status=200,
            mimetype="application/json"
        )
        
    except sqlite3.Error as e:
        print(e)
        return Response(
                        response=json.dumps({"message" : "Cannot Delete list"}),
                        status=401,
                        mimetype="applicatiion/json")    

