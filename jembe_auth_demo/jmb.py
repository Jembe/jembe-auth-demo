from flask_seasurf import SeaSurf 
from flask_session import Session
from jembe import Jembe


__all__ = ("jmb", "init_jembe")

jmb = Jembe()
csrf = SeaSurf()
sess = Session()


def init_jembe(app):
    csrf.init_app(app)
    sess.init_app(app)
    jmb.init_app(app)