from jembe_auth_demo.db import db

__all__ = ("Group",)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75), nullable=False)
    description = db.Column(db.Text)

    __table_args__ = dict(info=dict(verbose_name="Group", verbose_name_plural="Groups"))

    def __str__(self) -> str:
        return self.name
