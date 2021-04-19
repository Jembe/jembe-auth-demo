from typing import TYPE_CHECKING, Any, Optional, Dict
from jembe import Component, config, listener, action, JembeInitParamSupport
from dataclasses import dataclass, field, asdict

from jembe.component import component

if TYPE_CHECKING:
    from jembe import Event

__all__ = ("CConfirmationDialog", "Confirmation", "OnConfirmationMixin")


@dataclass
class Confirmation(JembeInitParamSupport):
    title: str
    question: str
    action: str
    params: dict = field(default_factory=dict)
    state: dict = field(default_factory=dict)
    force_init: bool = False

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
                state=value.get("state"),
                force_init=value.get("force_init"),
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
            if self.state.confirmation.force_init:  # type:ignore
                self.component(
                    self.state.source, **self.state.confirmation.state
                ).force_init()
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