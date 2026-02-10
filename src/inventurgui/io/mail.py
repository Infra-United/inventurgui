import smtplib
import ssl
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

from dotenv.variables import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

from inventurgui.helper.config import settings
from inventurgui.helper.i18n import i18n
from inventurgui.helper.logger import LOGGER
from inventurgui.helper.magic_link import get_magic_link
from inventurgui.io.cache import Cache
from inventurgui.io.request import convert_dates
from inventurgui.io.warehouse import Warehouse


class MailServer(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="UTF-8", env_prefix="MAIL_", extra="ignore")

    domain: str
    port: int
    user: str
    password: str


def send_mail(
    request: dict[str, str | dict[str, str]],
    warehouses: list[Warehouse],
    request_type: Literal["request", "update", "delete", "failure"],
    exception: Exception = None,
    mail_server: MailServer = MailServer(),
) -> None:
    LOGGER.debug("Connecting to SMTP Server...")
    email = request.get("email")
    with smtplib.SMTP_SSL(mail_server.domain, mail_server.port, context=ssl.create_default_context()) as smtp:
        smtp.ehlo()
        smtp.set_debuglevel(1)
        LOGGER.debug("Logging into SMTP Client with credentials...")
        smtp.login(mail_server.user, mail_server.password)
        mail = MIMEMultipart("mixed")
        mail.add_header("subject", create_subject(request, request_type))
        mail.add_header("from", f"{email.split('@')[0].capitalize()} <{email}>")
        mail.add_header("date", formatdate(localtime=True))
        mail.add_header("Message-ID", make_msgid())
        mail.add_header("Return-Path", mail_server.user)
        mail.add_header("reply-to", f"{email.split('@')[0].capitalize()} <{email}>")
        mail.attach(MIMEText(to_html(request, warehouses, exception), "html"))

        receiver = settings.mail["mail_to"] if not exception else settings.mail["admin"]
        mail["to"] = receiver
        LOGGER.debug(f"Sending E-Mail to {receiver}...")
        smtp.ehlo()
        smtp.sendmail(str(mail_server.user), receiver, mail.as_string())
        LOGGER.debug("Quitting Connection to SMTP Server...")
        smtp.quit()


def create_subject(
    request: dict[str, str | dict[str, str]], type: Literal["request", "update", "delete", "failure"]
) -> str:
    start, end, month, year = convert_dates(request.get("dates"))
    return f"[{i18n.get(f'mail_subject.{type}')}] {request.get('name')} {month} {year}"


def to_html(request: dict[str, str | dict[str, str]], warehouses: list[Warehouse], exception: Exception) -> str:
    html = ""
    magic_link = get_magic_link()
    for key, value in request.items():
        match key:
            case "dates":
                start, end, month, year = convert_dates(request.get("dates"))
                html += f"</br>{settings.form.get('start')}: {start}"
                html += f"</br>{settings.form.get('end')}: {end}"
                continue
            case "message" | "start" | "end":
                continue
            case "sent" | "updated" | "deleted":
                html += f"</br>{settings.form.get(key)}: {value}" if value else ""
            case _:
                if key in settings.form["input"].keys():
                    html += f"</br>{settings.form['input'].get(key)}: {value}"
    is_selected = [w.name for w in warehouses if Cache.selected(w.name) != []]
    html += f"</br></br>{settings.warehouse.get('label')}: {', '.join(is_selected)}"
    html += f"</br>{settings.form.get('update_link')}: <a href={magic_link}>{magic_link}</a>"
    html += f"</br></br>{settings.form['input'].get('message')}:</br></br>{request.get('message')}"
    if exception:
        html += f"</br></br>{exception.args[0]}: <br><br>{traceback.print_exc()}"
    return html
