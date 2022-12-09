import ast
from routes import app, version, redis_cli
import json
from flask import Response, request, jsonify
import sqlite3
from routes.user_action import token_required, database_locale


list_profile = ("listId", "listName", "listDescription", "imageName")

@app.route(f"{version}/createlist", methods=["POST"])
@token_required
def createlist(u_id):
    # getting list details from the form

    list_detatils = {
        "listName" : request.form["listName"],
        "listDescription" : request.form["listDescription"],
        "imageName" : request.form["imageName"]
    }

    try:
        # creating database connection and cursor
        conn = sqlite3.connect(database_locale)
        c = conn.cursor()
        c.execute("INSERT INTO list(listName, listDescription, imageName) VALUES (?, ?, ?)", (list_detatils["listName"], list_detatils["listDescription"], list_detatils["imageName"]))
        c.execute("SELECT listId FROM list ORDER BY listId DESC LIMIT 1")
        list_id = c.fetchone()
        c.execute("INSERT INTO creates(userId, listId) VALUES(?,?)",(u_id[0],list_id[0]))
        conn.commit()
        redis_cli.rpush(u_id[0], list_id[0])
        list_detatils["listId"] = list_id[0]
        redis_cli.set(f"list{list_id[0]}", json.dumps(list_detatils))
        conn.close()

        return Response(
            response=json.dumps({"message":f"{list_detatils['listName']} list is created"}),
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
            list_details["listId"] = listId
            redis_cli.set(f"list{listId}", json.dumps(list_details))
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

    resultArr = []
    try:
        if redis_cli.exists(u_id[0]):
            lists = redis_cli.lrange(u_id[0], 0, -1)
            for List in lists:
                resultArr.append(ast.literal_eval(redis_cli.get(f"list{List}")))
        else: 
            conn = sqlite3.connect(database_locale)
            c = conn.cursor()
            c.execute("select * from list where listId in (select c.listId from list l, creates c where l.listId = c.listId and c.userId = ?)", (u_id[0],))
            lists = c.fetchall()

            
            for lis in lists:
                if len(list_profile) == len(lis):
                    resultDict = {list_profile[i] : lis[i] for i, _ in enumerate(list_profile)}
                    redis_cli.rpush(u_id[0],lis[0])
                    redis_cli.set(f"list{lis[0]}", json.dumps(resultDict))
                    resultArr.append(resultDict)
                
            conn.commit()
            conn.close()
        return Response(
            response=json.dumps({"Lists": resultArr}),
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
        print("cache Hit")
        if redis_cli.exists(u_id[0]):
            List = ast.literal_eval(redis_cli.get(f"list{listId}"))
            return Response(
                response=json.dumps({"message": List}),
                status=200,
                mimetype="application/json"
            )
        else:
            conn = sqlite3.connect(database_locale)
            c = conn.cursor()
            c.execute("SELECT userId FROM creates WHERE listId=?",(listId,))
            userId = c.fetchone()

            if userId == u_id:
                c.execute("SELECT * FROM list WHERE listId = ?",(listId,))
                List = c.fetchone()
                if len(list_profile) == len(List):
                    resultDict = {list_profile[i] : List[i] for i, _ in enumerate(list_profile)}
                    redis_cli.rpush(u_id[0],List[0])
                    redis_cli.set(f"list{List[0]}", json.dumps(resultDict))
                    
            else:
                return Response(
                    response=json.dumps({"message": "Unauthorized access"}),
                    status=200,
                    mimetype="application/json"
                )

            conn.commit()
            conn.close()

            return Response(
            response=json.dumps({"message": resultDict}),
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
            conn.commit()
            c.execute("select * from list where listId in (select c.listId from list l, creates c where l.listId = c.listId and c.userId = ?)", (u_id[0],))
            lists = c.fetchall()
            
            redis_cli.delete(u_id[0])
            redis_cli.delete(f"list{listId}")
            for lis in lists:
                if len(list_profile) == len(lis):
                    resultDict = {list_profile[i] : lis[i] for i, _ in enumerate(list_profile)}
                    redis_cli.rpush(u_id[0],lis[0])
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

