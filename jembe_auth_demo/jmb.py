from jembe import Jembe

__all__ = ("jmb", "init_jembe")

jmb = Jembe()


def init_jembe(app):
    jmb.init_app(app)