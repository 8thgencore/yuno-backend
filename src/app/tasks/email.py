import asyncio

from celery import shared_task
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from loguru import logger

from app.core.config import settings


@shared_task(name="send_verification_email")
def send_verification_email(email_to: str, otp_code: int) -> None:
    email_body = {
        "email": email_to,
        "otp_code": str(otp_code),
    }
    message = MessageSchema(
        subject="Yuno Email Verification",
        recipients=[email_to],
        subtype=MessageType.html,
        template_body=email_body,
    )

    fm = FastMail(ConnectionConfig(**settings.mail.dict()))

    try:
        asyncio.run(fm.send_message(message, template_name="verification_email.html"))
        logger.info(f"Otp code has been successfully sent to e-mail: '{email_to}'")
    except Exception as e:
        logger.error(f"Not able to send email: '{e}'")
