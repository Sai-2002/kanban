from routes.monthly_report import dailyReport
import schedule
import time

def Scheduled():

    schedule.every(10).seconds.do(dailyReport)

    while True:
        print("scedhuler")
        schedule.run_pending()
        time.sleep(1)
