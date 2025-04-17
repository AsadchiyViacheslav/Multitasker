import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from fastapi import HTTPException
import logging


def send_reset_code_email(email_to: str, reset_code: str):
    # Настройки SMTP
    smtp_host = "smtp.yandex.ru"
    smtp_port = 465
    smtp_user = settings.SMTP_USER
    smtp_password = settings.SMTP_PASSWORD

    message = MIMEMultipart()
    message["From"] = smtp_user
    message["To"] = email_to
    message["Subject"] = "Код восстановления пароля для MultiTasker"

    body = f"""
    <h2>Восстановление пароля</h2>
    <p>Вы запросили восстановление пароля для аккаунта в MultiTasker.</p>
    <p>Ваш код восстановления: <strong>{reset_code}</strong></p>
    """

    message.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, email_to, message.as_string())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка отправки email: {str(e)}"
        )
