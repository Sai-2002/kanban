from routes import app, version
import json
from flask import Response, request, jsonify
import sqlite3
from routes.user_action import token_required, database_locale

@app.route(f"{version}/createCard/<listId>", methods=["POST"])
@token_required
def createCard(u_id, listId):

    card_detatils = {
        "name" : request.form["cardName"],
        "description" : request.form["cardDescription"],
        "deadLineDate" : request.form["deadLineDate"],
        "status" : "false"
    }

    try:
        # creating database connection and cursor
        conn = sqlite3.connect(database_locale)
        c = conn.cursor()
        c.execute("INSERT INTO card(cardName, cardDescription, deadLineDate, status) VALUES (?, ?, ?, ?)", (card_detatils["name"], card_detatils["description"], card_detatils["deadLineDate"], card_detatils["status"]))
        c.execute("SELECT cardId FROM card WHERE cardName=?", (card_detatils["name"],))
        card_id = c.fetchone()
        c.execute("INSERT INTO contains(listId, cardId) VALUES(?,?)",(listId,card_id[0]))
        conn.commit()
        conn.close()

        return Response(
            response=json.dumps({"message":f"{card_detatils['name']} card is created"}),
            status=200,
            mimetype="application/json"
        )
    except sqlite3.Error as e:
        print(e)
        return Response(
                        response=json.dumps({"message" : "Cannot create card"}),
                        status=401,
                        mimetype="applicatiion/json")


@app.route(f"{version}/getAllCard/<listId>", methods=["GET"])
@token_required
def getAllCard(u_id, listId):
    try:

        conn = sqlite3.connect(database_locale)
        c = conn.cursor()
        c.execute("select card.cardId, card.cardName, card.cardDescription, card.deadLineDate, card.status, contains.listId from card,contains where card.cardId = contains.cardId and card.cardId in (select c.cardId from card l, contains c where l.cardId = c.cardId and c.listId = ?);", (listId))
        cards = c.fetchall()
        conn.commit()
        conn.close()
        return Response(
            response=json.dumps({"message": f"{cards}"}),
            status=200,
            mimetype="application/json"
        )
    except:
        return Response(
            response=json.dumps({"message":"Cannot display all card"}),
            status=200,
            mimetype="application/json"
        )

@app.route(f"{version}/getCard/<listId>/<cardId>", methods=["GET"])
@token_required
def getCard(u_id, listId, cardId):
    try:
        conn = sqlite3.connect(database_locale)
        c = conn.cursor()
        c.execute("SELECT userId FROM creates WHERE listId=?",(listId,))
        userId = c.fetchone()

        if userId == u_id:
            c.execute("SELECT listId FROM contains WHERE listId = ?",(listId,))
            List = c.fetchone()
            if List[0] == int(listId):
                c.execute("SELECT * FROM card WHERE cardId = ?",(cardId,))
                card = c.fetchone()
                card = card + List
            else:
                return Response(
                    response=json.dumps({"message": "There is no such List."}),
                    status=200,
                    mimetype="application/json"
                )
        else:
            return Response(
                response=json.dumps({"message": "Unauthorized access"}),
                status=200,
                mimetype="application/json"
            )

        conn.commit()
        conn.close()

        return Response(
            response=json.dumps({"card": f"{card}"}),
            status=200,
            mimetype="application/json"
        )
        
    except sqlite3.Error as e:
        print(e)
        return Response(
                        response=json.dumps({"message" : "Cannot Display card"}),
                        status=401,
                        mimetype="applicatiion/json")


@app.route(f"{version}/updateCard/<listId>/<cardId>", methods=["POST"])
@token_required
def updateCard(u_id, listId, cardId):

    card_detatils = {
        "name" : request.form["cardName"],
        "description" : request.form["cardDescription"],
        "deadLineDate" : request.form["deadLineDate"],
        "status" : "false"
    }

    try:
        conn = sqlite3.connect(database_locale)
        c = conn.cursor()
        c.execute("SELECT userId FROM creates WHERE listId=?",(listId,))
        userId = c.fetchone()

        if userId == u_id:
            c.execute("SELECT listId FROM contains WHERE listId = ?",(listId,))
            List = c.fetchone()
            if List[0] == int(listId):
                c.execute("UPDATE card SET cardName = ?, cardDescription = ?, deadLineDate = ?, status = ? WHERE cardId = ?", (card_detatils["name"], card_detatils["description"], card_detatils["deadLineDate"], card_detatils["status"], cardId))
            else:
                return Response(
                    response=json.dumps({"message": "There is no such List."}),
                    status=200,
                    mimetype="application/json"
                )
        else:
            return Response(
                response=json.dumps({"message": "Unauthorized access"}),
                status=200,
                mimetype="application/json"
            )

        conn.commit()
        conn.close()

        return Response(
            response=json.dumps({"message": f"{card_detatils['name']} is updated"}),
            status=200,
            mimetype="application/json"
        )
        
    except sqlite3.Error as e:
        print(e)
        return Response(
                        response=json.dumps({"message" : "Cannot Update card"}),
                        status=401,
                        mimetype="applicatiion/json")

@app.route(f"{version}/deleteCard/<listId>/<cardId>", methods=["POST"])
@token_required
def deleteCard(u_id, listId, cardId):
    pass