import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime as datetimenow
import datetime

import utility

disclaimer_html = "Disclaimer: please note that we do not provide any tips/stock suggestion. All analysis is shared for educational purpose only."

def get_bcc_emails_from_file(filename: str) -> str:
    """
    Reads email addresses from a file (one per line), strips whitespace,
    and returns them as a comma-separated string.
    """
    try:
        with open(filename, 'r') as file:
            email_list = [line.strip() for line in file if line.strip()]
        return ",".join(email_list)
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return ""
    except Exception as e:
        print(f"Error reading emails from file: {e}")
        return ""

def sendEmail(emailTo, stock, price, target, stopLoss):
    try:
        dtLivedate,dtLiveTime12Hr = utility.getDateAndTimeIn12HrFormat()
        # Email and application-specific password for the Gmail account
        email = "shahuk23@gmail.com"
        # Recipient's email address
        #to_email = "thakkarhetal5@gmail.com"

        # Create message object instance
        msg = MIMEMultipart()

        # Email subject and message body
        msg['From'] = email
        msg['To'] = emailTo
        msg['BCC'] = get_bcc_emails_from_file('bcc_list.txt') #"shahuk23@gmail.com,thakkarhetal5@gmail.com,sayaliaher5495@gmail.com"
        msg['Subject'] = "✅ Stock alert: "+ stock +" "+ dtLivedate +" at "+dtLiveTime12Hr
        body = "Hello,\n\nAlgo ✅ Stock alert: "+ stock +"\nBuy at: "+ str(price) +",\nTarget: "+ str(target) +",\nstop loss: "+ str(stopLoss) +"+ \n\n\n"+disclaimer_html

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

        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)


def sendEmailAtEOD(maintain_unique_stocks):
    try:

        dtLivedate,dtLiveTime12Hr = utility.getDateAndTimeIn12HrFormat()
        # Email and application-specific password for the Gmail account
        email = "shahuk23@gmail.com"
        # Recipient's email address
        #to_email = "thakkarhetal5@gmail.com"

        # Create message object instance
        msg = MIMEMultipart()

        # Email subject and message body
        msg['From'] = email
        msg['To'] = email
        msg['BCC'] = "shahuk23@gmail.com,thakkarhetal5@gmail.com"
        msg['Subject'] = "✅ Stock EOD Report: "+ dtLivedate #+" at "+dtLiveTime12Hr+" IST"
        body = "<h3>✅ Stock EOD Closing Report</h3>"
        body += generate_html_stock_report(maintain_unique_stocks)

        # Attach the message body to the email
        msg.attach(MIMEText(body, 'html'))

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

        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)


def generate_html_stock_report(maintain_unique_stocks):
    disclaimer_html = (
        "<b>Disclaimer:</b> <i>Please note that we do not provide any tips or stock suggestions. "
        "All analysis is shared for educational purposes only.</i>"
    )

    # Begin HTML structure
    html_body = """
        <html>
        <head>
          <style>
            table {
              border-collapse: collapse;
              width: 100%;
              font-family: Arial, sans-serif;
            }
            th, td {
              border: 1px solid #ccc;
              padding: 8px;
              text-align: left;
            }
            th {
              background-color: #f2f2f2;
            }
            h3 {
              color: #333;
            }
          </style>
        </head>
        <body>         
          <table>
            <tr>
              <th>Stock</th>
              <th>Trigger Price ⬆️</th>
              <th>Date</th>
              <th>Time</th>
            </tr>
        """

    # Populate table rows
    for stock in maintain_unique_stocks:
        nsecode = stock.get('nsecode', 'N/A')
        close = stock.get('close', 'N/A')
        date = stock.get('date', 'N/A')
        time = stock.get('time', 'N/A')

        html_body += f"""
            <tr>
              <td>{nsecode}</td>
              <td>{close}</td>
              <td>{date}</td>
              <td>{time}</td>
            </tr>
            """

    # Close table and add disclaimer
    html_body += f"""
          </table>
          <br><br>
          {disclaimer_html}
        </body>
        </html>
        """

    return html_body


def sendEmailAlert(email_body_lines,stockTriggerDate,stockTriggerTime, source):
    try:

        #dtLivedate,dtLiveTime12Hr = utility.getDateAndTimeIn12HrFormat()
        # Email and application-specific password for the Gmail account
        email = "shahuk23@gmail.com"
        # Recipient's email address
        #to_email = "thakkarhetal5@gmail.com"

        # Create message object instance
        msg = MIMEMultipart()

        # Email subject and message body
        msg['From'] = email
        msg['To'] = email
        msg['BCC'] = "shahuk23@gmail.com,thakkarhetal5@gmail.com"#get_bcc_emails_from_file('bcc_list.txt') #"shahuk23@gmail.com,thakkarhetal5@gmail.com
        stock_csv = get_nsecode_csv(email_body_lines)
        #msg['Subject'] = "✅ Stock EOD Report: "+ dtLivedate +" at "+dtLiveTime12Hr+" IST"
        msg['Subject'] = "✅ Stock alert: "+ stock_csv +" on "+ stockTriggerDate #+" at "+stockTriggerTime+" IST"+
        body = "<h3>✅ Hello,<br>✅ Stock alert: </h3>"
        body += generate_html_stock_report_new(email_body_lines, stockTriggerDate, stockTriggerTime)
        body += "© 2025 [SK]. All rights reserved. via "+source

        # Attach the message body to the email
        msg.attach(MIMEText(body, 'html'))

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

        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)


def generate_html_stock_report_new(maintain_unique_stocks, dtLivedate, dtLiveTime12Hr ):
    disclaimer_html = (
        "<b>Disclaimer:</b> <i>Please note that we do not provide any tips or stock suggestions. "
        "All analysis is shared for educational purposes only.</i>"
    )

    html_body = f"""
        <html>
        <head>
          <style>
            table {{
              border-collapse: collapse;
              width: 100%;
              font-family: Arial, sans-serif;
            }}
            th, td {{
              border: 1px solid #ccc;
              padding: 8px;
              text-align: left;
            }}
            th {{
              background-color: #f2f2f2;
            }}
            .target {{
              color: green;
              font-weight: bold;
            }}
            .sl {{
              color: red;
              font-weight: bold;
            }}
            .trigger {{
              font-weight: bold;
              color: #333;
            }}
            h3 {{
              color: #333;
            }}
          </style>
        </head>
        <body>
          <h3>📈 Signal Trigger On: {dtLivedate}</h3><br>
          <table>
            <tr>
              <th>Stock</th>
              <th>Trigger Price 💰</th>
              <th>Target 🎯</th>
              <th>StopLoss 🛑</th>
              <th>Time</th>
            </tr>
    """

    for stock in maintain_unique_stocks:
        nsecode = stock.get('nsecode', 'N/A')
        close = stock.get('close', 'N/A')
        target = stock.get('target', 'N/A')
        sl = stock.get('sl', 'N/A')
        time = dtLiveTime12Hr if dtLiveTime12Hr+' IST' else 'N/A'

        html_body += f"""
            <tr>
              <td>{nsecode}</td>
              <td class="trigger">₹{close}</td>
              <td class="target">₹{target}</td>
              <td class="sl">₹{sl}</td>
              <td>{time}</td>
            </tr>
        """

    html_body += f"""
          </table>
          <br><br>
          {disclaimer_html}
        </body>
        </html>
    """

    return html_body

def get_nsecode_csv(email_body_lines):
    return ', '.join(stock['nsecode'] for stock in email_body_lines)

