import smtplib
import ssl
import traceback
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from enum import StrEnum
from pathlib import Path

from dotenv.variables import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

from inventurgui.helper.config import settings
from inventurgui.helper.dates import convert_dates
from inventurgui.helper.i18n import i18n
from inventurgui.helper.logger import LOGGER


class RequestType(StrEnum):
    request = "request"
    update = "update"
    delete = "delete"
    failure = "failure"

class MailServer(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="UTF-8", env_prefix="MAIL_", extra="ignore")

    domain: str
    port: int
    user: str
    password: str


def send_mail(
    request: dict[str, str | dict[str, str]],
    request_type: RequestType,
    filename: Path = None,
    exception: Exception = None,
    mail_server: MailServer = MailServer(),
    ) -> None:
    LOGGER.debug("Connecting to SMTP Server...")
    email = request.get("email")
    user_id = request.get("edit_link").split("=")[-1]
    with smtplib.SMTP_SSL(mail_server.domain, mail_server.port, context=ssl.create_default_context()) as smtp:
        smtp.ehlo()
        smtp.set_debuglevel(1)
        LOGGER.debug("Logging into SMTP Client with credentials...")
        smtp.login(mail_server.user, mail_server.password)
        mail = MIMEMultipart("mixed")
        mail.add_header("Subject", create_subject(request, request_type))
        mail.add_header("From", f"{email}")
        mail.add_header("Date", formatdate(localtime=True))
        mail.add_header("Message-ID", f"<{user_id}-{request.get(request_type)}@{mail_server.domain}>")
        if request_type != "request":
            mail.add_header("In-Reply-To", f"<{user_id}-{request.get(RequestType.request)}@{mail_server.domain}>")
            mail.add_header("References", f"<{user_id}-{request.get("request")}@{mail_server.domain}>")
        mail.add_header("Return-Path", mail_server.user)
        mail.add_header("Reply-To", f"{email}")
        #mail.attach(MIMEText(create_text("text", request, exception), "plain"))
        mail.attach(MIMEText(create_text("html", request, exception), "html"))
        if filename is not None:
            with open(filename, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={filename.name}")
            mail.attach(part)

        receiver = [settings.mail["mail_to"], request.get("email")] if not exception else [settings.mail["admin"]]
        mail.add_header("To", ", ".join(receiver))
        LOGGER.debug(f"Sending E-Mail to {receiver}...")
        smtp.ehlo()
        smtp.sendmail(str(mail_server.user), receiver, mail.as_string())
        LOGGER.debug("Quitting Connection to SMTP Server...")
        smtp.quit()


def create_subject(
    request: dict[str, str | dict[str, str]], rtype: RequestType) -> str:
    start, end, month, year = convert_dates(request.get("dates"))
    if rtype == RequestType.update or rtype == RequestType.delete:
        return f"Re: [{i18n.get(f'mail.{rtype}')}] {request.get('name')} {month} {year}"
    return f"[{i18n.get(f'mail.{rtype}')}] {request.get('name')} {month} {year}"


def create_text(ttype:Literal["text", "html"], request: dict[str, str | float | dict[str, str]], exception: Exception) -> str:
    newline = "\n" if ttype == "text" else "<br>"
    add:list[str]= []
    for key, value in request.items():
        match key:
            case "dates":
                start, end, month, year = convert_dates(request.get("dates"))
                add.append(f"{i18n.get('form.start')}: {start}")
                add.append(f"{i18n.get('form.end')}: {end}")
                continue
            case "message" | "start" | "end":
                continue
            case "request" | "update" | "delete":
                if value:
                    readable_dt = f"{datetime.fromtimestamp(value):{settings.date_format} {settings.time_format}}"
                    add.append(f"{i18n.get(f"mail.{key}")}: {readable_dt}")
            case "edit_link":
                if not request.get("delete"):
                    add.append(f"{i18n.get('finish.editing_link')}: <a href={value}>{value}</a>")
            case _:
                if key in settings.form["input"].keys():
                    add.append(f"{settings.form['input'].get(key)}: {value}")
    add.append(f"{newline}{newline}{settings.form.get('message')}: {newline}{newline}{request.get('message')}")
    add.append(newline)
    if exception:
        add.append(f"{newline}{newline}{[a for a in exception.args]}: {newline}{newline}{traceback.print_exc()}")

    return newline.join(add)
