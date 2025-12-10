import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

from pydantic_settings import BaseSettings, SettingsConfigDict

from inventurgui.helper.config import config
from inventurgui.helper.logger import LOGGER


class MailSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="UTF-8", env_prefix="MAIL_", extra="ignore")

    domain: str
    port: int
    user: str
    password: str


class Mail:
    @classmethod
    def send_mail(cls, html: str, txt: str, subject: str, email:str, settings: MailSettings = MailSettings()) -> None:
        LOGGER.debug("Connecting to SMTP Server...")
        with smtplib.SMTP_SSL(settings.domain, settings.port, context=ssl.create_default_context()) as smtp:
            smtp.ehlo()
            smtp.set_debuglevel(1)
            LOGGER.debug("Logging into SMTP Client with credentials...")
            smtp.login(settings.user, settings.password)
            mail = MIMEMultipart("alternative")
            mail.add_header("subject", subject)
            mail.add_header("from", f"{settings.user.split('@')[0].capitalize()} <{settings.user}>")
            mail.add_header("date", formatdate(localtime=True))
            mail.add_header("Message-ID", make_msgid())
            mail.add_header("Return-Path", "noreply-anfragen@infraunited.org")
            mail.add_header('reply-to', f"{email.split('@')[0].capitalize()} <{email}>")
            mail.attach(MIMEText(txt, "txt"))
            mail.attach(MIMEText(html, "html"))

            receiver = config["mail"]["mail_to"]
            mail["to"] = receiver
            LOGGER.debug(f"Sending E-Mail to {receiver}...")
            smtp.ehlo()
            smtp.sendmail(str(settings.user), receiver, mail.as_string())
            LOGGER.debug("Quitting Connection to SMTP Server...")
            smtp.quit()
