from jembe import Component, config

__all__ = ("MainMenu",)


@config(Component.Config(template="common/main_menu.html", changes_url=False))
class MainMenu(Component):
    pass