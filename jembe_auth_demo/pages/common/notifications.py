from dataclasses import dataclass
from uuid import uuid4
from typing import Dict, Optional
from jembe import Component, config, listener

__all__ = ("CNotifications", "CSystemErrorNotification", "Notification")


@config(
    Component.Config(
        template="common/system_error_notification.html", changes_url=False
    )
)
class CSystemErrorNotification(Component):
    pass


@dataclass
class Notification:
    message: str
    level: str = "info"


@config(Component.Config(changes_url=False, template="common/notifications.html"))
class CNotifications(Component):
    def __init__(self, notifications: Optional[Dict[str, Notification]] = None) -> None:
        if notifications is not None:
            # remove notifications id where notification[id] == None
            self.state.notifications = {
                id: n for id, n in notifications.items() if n is not None
            }
        else:
            self.state.notifications = dict()

        super().__init__()

    @listener(event="pushNotification")
    def on_push_notification(self, event):
        notification = event.params.get(
            "notification", Notification("Undefined message")
        )
        if isinstance(notification, str):
            notification = Notification(notification)
        self.state.notifications[str(uuid4())] = notification
