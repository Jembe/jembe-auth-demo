from typing import TYPE_CHECKING, Any, Optional
from jembe import Component, config, listener, action, JembeInitParamSupport
from dataclasses import dataclass, field, asdict

if TYPE_CHECKING:
    from jembe import Event

__all__ = ("CConfirmationDialog", "Confirmation", "OnConfirmationMixin")


@dataclass
class Confirmation(JembeInitParamSupport):
    title: str
    question: str
    action: str
    params: dict = field(default_factory=dict)

    @classmethod
    def dump_init_param(cls, value: "Confirmation") -> Any:
        return asdict(value)

    @classmethod
    def load_init_param(cls, value: Any) -> Any:
        return (
            Confirmation(
                title=value.get("title"),
                question=value.get("question"),
                action=value.get("action"),
                params=value.get("params"),
            )
            if value is not None
            else None
        )


@config(Component.Config(changes_url=False, template="common/confirmation.html"))
class CConfirmationDialog(Component):
    def __init__(
        self,
        confirmation: Optional[Confirmation] = None,
        source: Optional[str] = None,
    ) -> None:
        super().__init__()

    @listener(event="requestConfirmation")
    def on_request_confirmation(self, event: "Event"):
        self.state.confirmation = event.confirmation
        self.state.source = event.source_exec_name

    @action
    def choose(self, choice: str):
        if choice == "ok":
            self.emit(
                "confirmation",
                choice=choice,
                action=self.state.confirmation.action,
                action_params=self.state.confirmation.params,
            ).to(self.state.source)
        self.state.confirmation = None
        self.state.source = None


class OnConfirmationMixin:
    @listener(event="confirmation")
    def on_confirmation(self, event: "Event"):
        if hasattr(self, event.action):
            return getattr(self, event.action)(**event.action_params)

    def request_confirmation(self, action:str, title:str, question:str,action_params:Optional[dict]=None):
        if action_params is None:
            action_params = dict(confirmed=True)

        self.emit( # type:ignore
            "requestConfirmation",
            confirmation=Confirmation(
                title=title,
                question=question,
                action=action,
                params=action_params,
            ),
        )