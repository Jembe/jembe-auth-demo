from jembe import Component, config

__all__ = ("CProgressIndicator",)


@config(Component.Config(template="common/progress_indicator.html", changes_url=False))
class CProgressIndicator(Component):
    pass