import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

from nicegui import app
from pydantic_settings import BaseSettings, SettingsConfigDict

from inventurgui.helper.config import config, form, warehouse_conf
from inventurgui.helper.logger import LOGGER
from inventurgui.io.request import convert_dates
from inventurgui.io.warehouse import Warehouse


class MailSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="UTF-8", env_prefix="MAIL_", extra="ignore")

    domain: str
    port: int
    user: str
    password: str

def send_mail(request:dict[str,str|dict[str, str]],
              warehouses:list[Warehouse],
              magic_link:str,
              settings: MailSettings = MailSettings()) -> None:
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
        mail.attach(MIMEText(to_html(request, warehouses, magic_link), "html"))

        receiver = config["mail"]["mail_to"]
        mail["to"] = receiver
        LOGGER.debug(f"Sending E-Mail to {receiver}...")
        smtp.ehlo()
        smtp.sendmail(str(settings.user), receiver, mail.as_string())
        LOGGER.debug("Quitting Connection to SMTP Server...")
        smtp.quit()

def create_subject(request:dict[str,str|dict[str, str]]) -> str:
    start, end, month, year = convert_dates(request.get('dates'))
    if request.get('sent'):
        return f"{config["mail"]["subject_update"]} {request.get('name')} {month} {year}"
    return f"{config["mail"]["subject_request"]} {request.get('name')} {month} {year}"

def to_html(request: dict[str, str|dict[str, str]], warehouses:list[Warehouse], magic_link:str) -> str:
    html = ""
    for key, value in request.items():
        match key:
            case 'dates':
                start, end, month, year = convert_dates(request.get('dates'))
                html += f"</br>{form.get('start')}: {start}"
                html += f"</br>{form.get('end')}: {end}"
                continue
            case 'message' | 'start' | 'end':
                continue
            case 'sent' | 'updated':
                html += f"</br>{form.get(key)}: {value}" if value else ''
            case _:
                html += f"</br>{form['input'].get(key)}: {value}"
    is_selected = [w.name for w in warehouses if app.storage.user.get(w.name) != []]
    html += f"</br></br>{warehouse_conf.get('label')}: {", ".join(is_selected)}"
    html += f"</br>{form.get('update_link')}: <a href={magic_link}>{magic_link}</a>"
    html += f"</br></br>{form.get('message')}:</br></br>{request.get('message')}"
    return html