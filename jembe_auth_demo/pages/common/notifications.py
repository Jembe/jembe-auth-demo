from jembe import Component, config

__all__ = ("Notifications", "SystemErrorNotification")


@config(Component.Config(template="common/notifications.html", changes_url=False))
class Notifications(Component):
    pass


@config(Component.Config(template="common/system_error_notification.html", changes_url=False))
class SystemErrorNotification(Component):
    pass