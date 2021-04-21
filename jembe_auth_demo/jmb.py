from flask_seasurf import SeaSurf 
from jembe import Jembe

__all__ = ("jmb", "csrf", "init_jembe")

jmb = Jembe()
csrf = SeaSurf()


def init_jembe(app):
    csrf.init_app(app)
    jmb.init_app(app)