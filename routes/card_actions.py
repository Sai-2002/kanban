from routes import app, version, redis_cli
import ast
import json
from flask import Response, request, jsonify
import sqlite3
from routes.user_action import token_required, database_locale


card_profile = ("cardId", "cardName","cardDescription", "deadLineDate", "status", "listId")

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

        c.execute("SELECT * FROM creates WHERE listId = ?", (listId,))
        List_id = c.fetchone()

        if not (List_id[0] == u_id[0] and List_id[1] == int(listId)):
            return Response(
                        response=json.dumps({"message" : "Cannot create card"}),
                        status=401,
                        mimetype="applicatiion/json")
        else:
            c.execute("INSERT INTO card(cardName, cardDescription, deadLineDate, status) VALUES (?, ?, ?, ?)", (card_detatils["name"], card_detatils["description"], card_detatils["deadLineDate"], card_detatils["status"]))
            c.execute("SELECT cardId FROM card ORDER BY cardId DESC LIMIT 1")
            card_id = c.fetchone()
            c.execute("INSERT INTO contains(listId, cardId) VALUES(?,?)",(listId,card_id[0]))
            conn.commit()

            redis_cli.rpush(f"listId{listId}", card_id[0])
            card_detatils["cardId"] = card_id[0]
            card_detatils["listId"] = listId
            redis_cli.set(f"card{card_id[0]}", json.dumps(card_detatils))
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
    
    resultArr = []
    
    try:
        if redis_cli.exists(f"listId{listId}"):
            cards = redis_cli.lrange(f"listId{listId}", 0, -1)
            for card in cards:
                resultArr.append(ast.literal_eval(redis_cli.get(f"card{card}")))

        else:
            conn = sqlite3.connect(database_locale)
            c = conn.cursor()
            c.execute("select card.cardId, card.cardName, card.cardDescription, card.deadLineDate, card.status, contains.listId from card,contains where card.cardId = contains.cardId and card.cardId in (select c.cardId from card l, contains c where l.cardId = c.cardId and c.listId = ?)", (listId,))
            cards = c.fetchall()
            for card in cards:
                if len(card_profile) == len(card):
                    resultDict = {card_profile[i] : card[i] for i, _ in enumerate(card_profile)}
                    redis_cli.rpush(f"listId{listId}", card[0])
                    redis_cli.set(f"card{card[0]}", json.dumps(resultDict))
                    resultArr.append(resultDict)

            conn.commit()
            conn.close()
            
        return Response(
            response=json.dumps({"message": resultArr}),
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

        if redis_cli.exists(f"user{u_id[0]}") and redis_cli.exists(f"listId{listId}") and redis_cli.exists(f"card{cardId}"):
            card = ast.literal_eval(redis_cli.get(f"card{cardId}"))
            return Response(
                response=json.dumps({"card": card}),
                status=200,
                mimetype="application/json"
        )
        else:
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

                    if len(card_profile) == len(card):
                        resultDict = {card_profile[i] : card[i] for i, _ in enumerate(card_profile)}
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
                response=json.dumps({"card": resultDict}),
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
        "listId" : request.form["listName"],
        "status" : request.form["status"]
    }

    try:
        conn = sqlite3.connect(database_locale)
        c = conn.cursor()
        c.execute("SELECT userId FROM creates WHERE listId=?",(listId,))
        userId = c.fetchone()

        if userId == u_id:
            c.execute("SELECT listId FROM contains WHERE listId = ?",(listId,))
            List = c.fetchone()
            c.execute("SELECT listId FROM list WHERE listId = ?",(card_detatils["listId"],))
            LISt = c.fetchone();

            if List and LISt:

                c.execute("UPDATE card SET cardName = ?, cardDescription = ?, deadLineDate = ?, status = ? WHERE cardId = ?", (card_detatils["name"], card_detatils["description"], card_detatils["deadLineDate"], card_detatils["status"], cardId))
                c.execute("UPDATE contains SET listId = ? WHERE cardId = ?",(LISt[0], cardId))
                conn.commit()

                c.execute("SELECT cardId FROM contains WHERE listId = ?", (listId,))
                card_Id = c.fetchall()


                redis_cli.delete(f"listId{listId}")
                redis_cli.delete(f"card{cardId}")

                for card in card_Id:
                    for c in card:
                        redis_cli.rpush(f"listId{listId}", c)
                
                if List[0] != LISt[0]:
                    redis_cli.rpush(f"listId{card_detatils['listId']}", cardId)

                card_detatils["cardId"] = cardId
                redis_cli.set(f"card{card_Id}", json.dumps(card_detatils))

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
    try:
        conn = sqlite3.connect(database_locale)
        c = conn.cursor()
        c.execute("SELECT userId FROM creates WHERE listId=?",(listId,))
        userId = c.fetchone()

        if userId == u_id:
            c.execute("SELECT listId FROM contains WHERE listId = ?",(listId,))
            List = c.fetchone()
            
            if List[0] == int(listId):
                c.execute("DELETE FROM card WHERE cardId = ?",(cardId,))
                c.execute("DELETE FROM contains WHERE cardId =?",(cardId,))

                c.execute("SELECT cardId FROM contains WHERE listId = ?", (listId,))
                card_Id = c.fetchall()

                redis_cli.delete(f"listId{listId}")

                for card in card_Id:
                    for c in card:
                        redis_cli.rpush(f"listId{listId}", c)

                redis_cli.delete(f"card{cardId}")

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
            response=json.dumps({"message": f"The card is deleted"}),
            status=200,
            mimetype="application/json"
        )
        
    except sqlite3.Error as e:
        print(e)
        return Response(
                        response=json.dumps({"message" : "Cannot delete card"}),
                        status=401,
                        mimetype="applicatiion/json")


@app.route(f"{version}/getCardCount/<listId>", methods=["GET"])
@token_required
def getCardCount(u_id, listId):
    
    total_count = 0
    completed_card = 0 

    try:
        if redis_cli.exists(f"listId{listId}"):
            cards = redis_cli.lrange(f"listId{listId}", 0, -1)
            total_count = len(cards)
            for card in cards:
                resultArr = ast.literal_eval(redis_cli.get(f"card{card}"))
                if(resultArr['status'] != 'false'):
                    completed_card = completed_card+1    

        else:
            conn = sqlite3.connect(database_locale)
            c = conn.cursor()
            c.execute("select card.cardId, card.cardName, card.cardDescription, card.deadLineDate, card.status, contains.listId from card,contains where card.cardId = contains.cardId and card.cardId in (select c.cardId from card l, contains c where l.cardId = c.cardId and c.listId = ?);", (listId,))
            cards = c.fetchall()

            total_count = len(cards)
            for card in cards:
                if len(card_profile) == len(card):
                    resultDict = {card_profile[i] : card[i] for i, _ in enumerate(card_profile)}
                    if(resultDict['status'] != 'false'):
                        completed_card = completed_card+1
                    
            conn.commit()
            conn.close()
            
        return Response(
            response=json.dumps({"total_cards": total_count, "completed_card" : completed_card, "incomplete_card" : total_count-completed_card}),
            status=200,
            mimetype="application/json"
        )
    except:
        return Response(
            response=json.dumps({"message":"Cannot display all card"}),
            status=200,
            mimetype="application/json"
        )
