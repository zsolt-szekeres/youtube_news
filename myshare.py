import config

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


def send_email(message, info):

    # Config sending email
    SENDER_EMAIL = config.params["email"]["sender_email"]
    RECEIVER_EMAILS = config.params["email"]["receiver_emails"]
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(SENDER_EMAIL, config.params["auth_codes"]["GMAIL_two_factor_password"])

    # Config email content
    subject = "[Youtube insights] - " + info["title"]
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECEIVER_EMAILS)
    msg["Subject"] = subject
    #'<p> View count: '+info['view_count']+"</p>" + \
    try:
        message = (
            '<p> <a href="'
            + info["webpage_url"]
            + '">'
            + info["webpage_url"]
            + "</a></p>"
            "<p> Duration: " + info["duration_string"] + "</p>" + message
        )
    except:
        print("No youtube link")

    message = "<html>" + message + "</html>"
    msg.attach(MIMEText(message, "html"))

    # Attach config
    with open("config.json", "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {'config.json'}")
        msg.attach(part)

    server.sendmail(SENDER_EMAIL, RECEIVER_EMAILS, msg.as_string())
    server.quit()
