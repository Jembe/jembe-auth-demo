from sqlalchemy.ext.associationproxy import association_proxy
from werkzeug.security import check_password_hash, generate_password_hash
from jembe_auth_demo.db import db
from flask_login import UserMixin
import sqlalchemy as sa

__all__ = (
    "User",
    "Group",
)

users_groups = db.Table(
    "users_groups",
    sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), primary_key=True),
    sa.Column("group_id", sa.Integer, sa.ForeignKey("groups.id"), primary_key=True),
)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    __table_args__ = dict(info=dict(verbose_name="User", verbose_name_plurkal="Users"))

    id = sa.Column(sa.Integer, primary_key=True)
    active = sa.Column(
        sa.Boolean, nullable=False, default=True, server_default=sa.true()
    )

    # authorization
    email = sa.Column(sa.String(255, collation="NOCASE"), nullable=False, unique=True)
    email_confirmed_at = sa.Column(sa.DateTime)
    password = sa.Column(sa.String(255), nullable=False, server_default="", default="")

    # user info
    first_name = sa.Column(sa.String(75), nullable=False, server_default="", default="")
    last_name = sa.Column(sa.String(75), nullable=False, server_default="", default="")

    # groups
    groups = sa.orm.relationship(
        "Group",
        secondary=users_groups,
        lazy="subquery",
        backref=sa.orm.backref("users", lazy=True),
    )
    # hmmm...
    groups_ids = association_proxy(
        "groups", "id", creator=lambda id: db.session.query(Group).get(id)
    )

    @property
    def is_active(self):
        return self.active

    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __str__(self) -> str:
        return "{} {}".format(self.first_name, self.last_name)


class Group(db.Model):
    __tablename__ = "groups"
    __table_args__ = dict(info=dict(verbose_name="Group", verbose_name_plural="Groups"))

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), nullable=False, unique=True)
    title = sa.Column(sa.String(255), nullable=False, unique=True)
    description = sa.Column(sa.Text)

    # hmmm....
    users_ids = association_proxy(
        "users", "id", creator=lambda id: db.session.query(User).get(id)
    )

    def __str__(self) -> str:
        return self.title
