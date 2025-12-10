from dataclasses import dataclass

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
        return f"{self.name} {self.start} - {self.end}"

    @property
    def html(self) -> str:
        return f"{self.name} {self.start} - {self.end}"