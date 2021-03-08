from jembe import Component, config

__all__ = ("Confirmation",)


@config(Component.Config(template="common/confirmation.html", changes_url=False))
class Confirmation(Component):
    pass