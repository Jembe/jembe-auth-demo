from jembe import Component, config

__all__ = ("Notifications",)


@config(Component.Config(template="common/notifications.html", changes_url=False))
class Notifications(Component):
    pass