from jembe import Component,config

__all__ = ("Dashboard",)


@config(Component.Config(changes_url=False))
class Dashboard(Component):
    pass