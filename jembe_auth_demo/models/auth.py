from jembe_auth_demo.db import db
from sqlalchemy.sql.expression import true

__all__ = (
    "User",
    "Group",
)

user_groups = db.Table(
    "user_group",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("group_id", db.Integer, db.ForeignKey("groups.id"), primary_key=True),
)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(
        db.Boolean(),
        nullable=False,
        server_default=true(),
        default=True,
    )

    # authorization
    email = db.Column(db.String(255, collation="NOCASE"), nullable=False, unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default="", default="")

    # user info
    first_name = db.Column(
        db.String(100, collation="NOCASE"), nullable=False, server_default=""
    )
    last_name = db.Column(
        db.String(100, collation="NOCASE"), nullable=False, server_default=""
    )

    # groups
    groups = db.relationship(
        "Group",
        secondary=user_groups,
        lazy="subquery",
        backref=db.backref("users", lazy=True),
    )

    __table_args__ = dict(info=dict(verbose_name="User", verbose_name_plurkal="Users"))

    def __str__(self) -> str:
        return "{} {}".format(self.first_name, self.last_name)


class Group(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75), nullable=False)
    title = db.Column(db.String(75), nullable=False)
    description = db.Column(db.Text)

    __table_args__ = dict(info=dict(verbose_name="Group", verbose_name_plural="Groups"))

    def __str__(self) -> str:
        return self.title
