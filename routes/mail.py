from email.message import EmailMessage
import ssl
import smtplib


password = 'zgrvoiyhlakufypd'

def newMake(emailaddr, body):
    em = EmailMessage()
    em['From'] = 'smnjr2002@gmail.com'
    em['To'] = emailaddr
    em['Subject'] = "Report!!!"
    em.set_content(body)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context= context) as smtp:
        smtp.login('smnjr2002@gmail.com', password)
        smtp.sendmail('smnjr2002@gmail.com', emailaddr, em.as_string())
