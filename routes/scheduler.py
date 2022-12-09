from routes.monthly_report import dailyReport
import schedule
import time

def Scheduled():
    
    schedule.every().day.at("05:00").do(dailyReport)
    
    while True:
        schedule.run_pending()
        time.sleep(1)