import smtplib
from email.message import EmailMessage
from app.core.config import settings

def send_verification_email(to_email: str, token: str):
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    message = EmailMessage()
    message["Subject"] = "Verify your email"
    message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
    message["To"] = to_email
    message.set_content(f"Click the link to verify your email: {link}")

    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
        server.starttls()
        server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
        server.send_message(message)
