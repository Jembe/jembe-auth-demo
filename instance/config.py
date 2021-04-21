import os

instance_path = os.environ.get(
    "FLASK_INSTANCE_PATH", os.path.join(os.getcwd(), "instance")
)

SQLALCHEMY_DATABASE_URI = "sqlite:///../data/jembe_auth_demo.sqlite"
SQLALCHEMY_TRACK_MODIFICATIONS = False
JEMBE_UPLOAD_FOLDER = "../data/media"
# CSRF_COOKIE_PATH = ""
# APPLICATION_ROOT = ""
SECRET_KEY = b"\xeb\x13\xa0=\x04\xa5i!\xafd\x96\xc5\x07\xf0,k1\n\xfc\xf64\x08C\xe8"
SESSION_TYPE = "filesystem"
SESSION_FILE_DIR = os.path.join(instance_path, "../data/flask_session")
