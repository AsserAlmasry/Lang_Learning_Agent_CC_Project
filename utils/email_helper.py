import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.config import Config

def send_feedback_email(subject, body):
    """
    Sends an email using Gmail SMTP.
    Requires a Gmail App Password.
    """
    if not Config.SENDER_EMAIL or not Config.SENDER_PASSWORD:
        return False, "Email credentials not configured."

    try:
        msg = MIMEMultipart()
        msg['From'] = Config.SENDER_EMAIL
        msg['To'] = Config.RECIPIENT_EMAIL or Config.SENDER_EMAIL
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        # Connect to Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(Config.SENDER_EMAIL, Config.SENDER_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(Config.SENDER_EMAIL, msg['To'], text)
        server.quit()
        
        return True, "Email sent successfully."
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"
