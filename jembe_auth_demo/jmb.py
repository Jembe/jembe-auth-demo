from flask_seasurf import SeaSurf
from flask_session import Session
from flask_login import LoginManager
from jembe import Jembe
from .models import User
from .db import db


__all__ = ("jmb", "init_jembe")

jmb = Jembe()
csrf = SeaSurf()
sess = Session()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    """Reloads the user object from the user ID stored in the session"""
    if user_id is not None:
        return db.session.query(User).get(user_id)
    return None

def init_jembe(app):
    csrf.init_app(app)
    sess.init_app(app)
    login_manager.init_app(app)
    jmb.init_app(app)