from jembe_auth_demo.db.exc_filters import handler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import event

__all__ = ("db", "init_db")

db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)
    event.listen(db.get_engine(app), "handle_error", handler)