import datetime
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

from pydantic_settings import BaseSettings, SettingsConfigDict

from inventurgui.helper.config import config, form
from inventurgui.helper.logger import LOGGER


class MailSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="UTF-8", env_prefix="MAIL_", extra="ignore")

    domain: str
    port: int
    user: str
    password: str

def send_mail(request:dict[str,str], settings: MailSettings = MailSettings()) -> None:
    LOGGER.debug("Connecting to SMTP Server...")
    email = request.get("email")
    with smtplib.SMTP_SSL(settings.domain, settings.port, context=ssl.create_default_context()) as smtp:
        smtp.ehlo()
        smtp.set_debuglevel(1)
        LOGGER.debug("Logging into SMTP Client with credentials...")
        smtp.login(settings.user, settings.password)
        mail = MIMEMultipart("mixed")
        mail.add_header("subject", create_subject(request))
        mail.add_header("from", f"{email.split('@')[0].capitalize()} <{email}>")
        mail.add_header("date", formatdate(localtime=True))
        mail.add_header("Message-ID", make_msgid())
        mail.add_header("Return-Path", settings.user)
        mail.add_header('reply-to', f"{email.split('@')[0].capitalize()} <{email}>")
        mail.attach(MIMEText(to_html(request), "html"))

        receiver = config["mail"]["mail_to"]
        mail["to"] = receiver
        LOGGER.debug(f"Sending E-Mail to {receiver}...")
        smtp.ehlo()
        smtp.sendmail(str(settings.user), receiver, mail.as_string())
        LOGGER.debug("Quitting Connection to SMTP Server...")
        smtp.quit()

def create_subject(request:dict[str,str|dict[str,str]]) -> str:
    return (f"{config["mail"]["subject"]} {request.get('name')} "
            f"{datetime.date.fromisoformat(request['dates'].get('from')):%d.%m.%Y} - "
            f"{datetime.date.fromisoformat(request['dates'].get('to')):%d.%m.%Y}")

def to_html(request: dict[str, str|dict[str, str]]) -> str:
    html = ""
    for key, value in request.items():
        match key:
            case 'dates':
                html += f"</br>{form.get('start')}: {datetime.date.fromisoformat(value.get('from')):%d.%m.%Y}"
                html += f"</br>{form.get('end')}: {datetime.date.fromisoformat(value.get('to')):%d.%m.%Y}"
                continue
            case 'email':
                html += f"</br>{form.get('email')}: {value}"
            case 'message' | 'start' | 'end':
                continue
            case _:
                html += f"</br>{form['input'].get(key)}: {value}"
    html += f"</br></br>Nachricht:</br>{request.get('message')}"
    return html