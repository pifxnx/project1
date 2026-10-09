import smtplib
from email.message import EmailMessage

from pathlib import Path

from ..core.config import settings


def send_email(to: str, subject: str, body: str, file_path: Path) -> None:
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    if file_path.suffix == ".pdf":
        maintype = "application"
        subtype = "pdf"
    elif file_path.suffix == ".xlsx":
        maintype = "application"
        subtype = "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        raise ValueError("Unsupported file type")

    with file_path.open("rb") as f:
        message.add_attachment(
            f.read(), maintype=maintype, subtype=subtype, filename=file_path.name
        )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        if settings.smtp_starttls:
            smtp.starttls()
        if settings.smtp_login:
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(message)
