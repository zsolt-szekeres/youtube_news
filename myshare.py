import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(message, subject_spec, yt_link=None):
    
    # Set the sender's and receiver's email addresses
    sender_email = os.getenv("GMAIL_EMAIL")
    receiver_email = os.getenv("GMAIL_EMAIL")

    # Set the password for your email account (generated app password for two-factor authentication)
    password = os.getenv("GMAIL_TWOFACTOR")

    # Set the subject and message for the email
    subject = "[Youtube insights] - " + subject_spec
    
    # Set up the SMTP server
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Create a secure connection to the SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()

    # Log in to the sender's email account
    server.login(sender_email, password)

    # Create a multipart message and set the headers
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # Attach the message to the email
    if yt_link:
        message = '<p> <a href="'+yt_link+'">'+yt_link +'</a> </p>' + message
    message = "<html>"+message+"</html>"
    msg.attach(MIMEText(message, "html"))

    # Send the email
    server.sendmail(sender_email, receiver_email, msg.as_string())

    # Close the SMTP server connection
    server.quit()





