
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from app.core.config import settings

# def send_verification_email(to_email: str, token: str):
#     msg = MIMEMultipart("alternative")
#     msg["Subject"] = "Verify your email"
#     msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
#     msg["To"] = to_email

#     verify_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"

#     html = f"""
#     <html>
#         <body>
#             <p>Hi,<br>
#             Please verify your email by clicking the link below:<br>
#             <a href="{verify_link}">Verify Email</a>
#             </p>
#         </body>
#     </html>
#     """

#     msg.attach(MIMEText(html, "html"))

#     with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
#         server.starttls()
#         server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
#         server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
