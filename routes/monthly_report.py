from routes.user_action import database_locale
import sqlite3
from datetime import datetime
from routes.mail import newMake
def dailyReport():
    print("llll")
    try:
        conn = sqlite3.connect(database_locale)
        c = conn.cursor()
        c.execute("SELECT userId, gmail, userName FROM user")
        userDetails = c.fetchall()
        for user in userDetails:
            nCompleted = 0
            not_completed = []
            due = []
            total_cards = 0
            
            emailAddr = user[1]
            c.execute("SELECT listId from creates where userId = ?", (user[0],))

            listId = c.fetchall()

            if(datetime.now().day == 1):
                newMake(emailaddr=emailAddr, body=monthlyReport(userName= user[2],listId=listId))
                

            for List in listId:
                c.execute("SELECT cardId from contains where listId = ?", List)
                cardsId = c.fetchall()
                total_cards = len(cardsId)
                for card in cardsId:
                    c.execute("SELECT cardName, deadLineDate, status from card where cardId = ?", card)
                    Card = c.fetchone()
                    if Card[2] == "false":
                        not_completed.append(Card[0])
                        nCompleted = nCompleted+1
                        deadLine = Card[1]
                        if deadLine > str(datetime.now()):
                            due.append(Card[0])
            
            
            body = f"""Hi {user[2]}. Todays report!!!!!!!
            There is/are {total_cards} total cards in which {nCompleted} is/are not completed.
            There is/are also due's which is/are {due}.
            Please Kindly finish the job and update in the app.
            Have a great day!! 
            """

            newMake(emailAddr, body=body)

                        
    except:
        print("ERROR!!!")
        

def monthlyReport(userName, listId):

    Completed = []
    nCompleted = 0
    total_cards = 0
    total_list = len(listId)
    try:
        conn = sqlite3.connect(database=database_locale)
        c = conn.cursor()
        for List in listId:
            c.execute(f"SELECT c.cardName, c.deadLineDate, c.status from card c, contains ca where ca.listId = ? and ca.cardId = c.cardId and c.cardId  in (SELECT cardId from card where cardCreatedDate LIKE '{datetime.now().year}-{datetime.now().month}-%')", (List,))
            
            Card = c.fetchall()

            total_cards = len(Card)

            for card in Card:
                if card[2] == "false":
                    nCompleted = nCompleted+1
                else:
                    Completed.append(Card[0])
            

        body = f"""Hi {userName}. Monthly report!!!!!!!
            There is/are {total_list} total list created in which {total_cards} where crearted this month.
            Among those cards {nCompleted} is/are not completed.
            The completed cards are {Completed}.
            Please Kindly finish the job and update in the app.
            Have a great start!! 
            """    

        return body
    except:
        print("ERROR!!!!")

