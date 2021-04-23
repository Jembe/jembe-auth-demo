import os
from flask import Flask
from . import jmb, db


def create_app(config=None):
    from . import models, views, pages, commands

    app = Flask(__name__, instance_relative_config=True)
    # make csrf cookie valid for whole session
    app.config.from_mapping({"CSRF_COOKIE_TIMEOUT": None})
    if config is not None:
        if isinstance(config, dict):
            app.config.from_mapping(config)
        elif config.endswith(".py"):
            app.config.from_pyfile(config)
    else:
        app.config.from_pyfile("config.py", silent=True)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_db(app)
    jmb.init_jembe(app)
    views.init_views(app)
    commands.init_commands(app)

    return app