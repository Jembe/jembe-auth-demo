from typing import TYPE_CHECKING
from jembe import Component, listener
from jembe.exceptions import JembeError

if TYPE_CHECKING:
    from jembe import Event, DisplayResponse


__all__ = ("PComponent",)


class PComponent(Component):
    class Config(Component.Config):
        pass

    _config = Config

    def init(self):
        if "active" not in self.state:
            raise JembeError(
                "Permenenet compoment must have active:bool=False state variable defined in __init__"
            )
        return super().init()

    @listener(event="activate")
    def on_activate(self, event: "Event"):
        self.state.active = True

    @listener(event="deactivate")
    def on_deactivate(self, event: "Event"):
        self.state.active = False

    def display(self) -> "DisplayResponse":
        if self.state.active:
            return super().display()
        return ""
