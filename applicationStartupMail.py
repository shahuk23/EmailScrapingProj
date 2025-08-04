import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime as datetimenow
from os import utime

import utility

disclaimer_html = "Disclaimer: please note that we do not provide any tips/stock suggestion. All analysis is shared for educational purpose only."

def sendEmailOnStart():
    try:
        email = "shahuk23@gmail.com"
        msg = MIMEMultipart()
        dtLivedate,dtLiveTime12Hr = utility.getDateAndTimeIn12HrFormat()
        msg['From'] = email
        msg['To'] = email
        msg['Subject'] = "🚀 Success! Stock Scanning Action has been triggered."+ dtLivedate #+" at "+dtLiveTime12Hr+" IST"
        body = "🚀 Success! Stock Scanning Action has been triggered. \n\n\n"+disclaimer_html

        # Attach the message body to the email
        msg.attach(MIMEText(body, 'plain'))

        # Connect to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        # Login to Gmail account using the application-specific password
        #https://myaccount.google.com/apppasswords?rapt=AEjHL4PPn88yysBS9Ty1TgzCycrb0wsa9W1ra5zDCjThy0pEtMlkZLPYppfMcu3bYdacrwYzW3s-ZgXSUqgnvkMLU_doJHI7eo7x62COanUZdGLcxMVcTfA
        #search "google app password" google and login.
        app_password = 'xwum bcbs gatc ykmk'
        server.login(email, app_password)

        # Send email
        server.send_message(msg)

        # Quit SMTP server
        server.quit()

        print("Startup Mail Email sent successfully!")
    except Exception as e:
        print("Startup Mail Failed to send:", e)

#if __name__ == "__main__":
#    sendEmailOnStart()

