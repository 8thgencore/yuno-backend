import grpc
from celery import shared_task
from loguru import logger

from app.core.config import settings
from app.generated.mail.mail_pb2 import SendEmailWithOTPCodeRequest
from app.generated.mail.mail_pb2_grpc import MailServiceStub


@shared_task(name="send_verification_email")
def send_verification_email(email_to: str, otp_code: int) -> None:
    # Create a gRPC channel
    channel = grpc.insecure_channel(f"{settings.mail.MAIL_HOST}:{settings.mail.MAIL_PORT}")

    # Create a gRPC stub for the Mail service
    stub = MailServiceStub(channel)

    # Prepare the request message
    request = SendEmailWithOTPCodeRequest(email=email_to, otp_code=str(otp_code))

    try:
        # Call the SendConfirmationEmail RPC
        response = stub.SendConfirmationEmailOTPCode(request)

        # Log success or failure
        if response.success:
            logger.info(f"Otp code has been successfully sent to e-mail: '{email_to}'")
        else:
            logger.error("Failed to send confirmation email.")
    except Exception as e:
        logger.error(f"Not able to send email: '{e}'")
    finally:
        # Close the gRPC channel
        channel.close()
