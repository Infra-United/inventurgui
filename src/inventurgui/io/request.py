from dataclasses import dataclass

from inventurgui.helper.config import config


@dataclass
class Request:
    name: str = ''
    place: str = ''
    start: str = ''
    end: str = ''
    email: str = ''
    donation: str = ''
    message: str = ''
    checkbox: bool = False

    @property
    def subject(self) -> str:
        return f"[{self.name}] {self.start} - {self.end}"

    @property
    def text(self) -> str:
        text = f"\n{config['form']['name']}: {self.name}"
        text += f"\n{config['form']['place']}: {self.place}"
        text += f"\n{config['form']['start']}: {self.start}"
        text += f"\n{config['form']['end']}: {self.end}"
        text += f"\n{config['form']['email']}: {self.email}"
        text += f"\n{config['form']['donation']}: {self.donation}"
        text += f"\n\n{self.message}"
        return text

    @property
    def html(self) -> str:
        html = f"</br>{config['form']['name']}: {self.name}"
        html += f"</br>{config['form']['place']}: {self.place}"
        html += f"</br>{config['form']['start']}: {self.start}"
        html += f"</br>{config['form']['end']}: {self.end}"
        html += f"</br>{config['form']['email']}: {self.email}"
        html += f"</br>{config['form']['donation']}: {self.donation}"
        html += f"</br></br>{self.message}"
        return html