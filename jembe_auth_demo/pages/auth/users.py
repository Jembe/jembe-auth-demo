from jembe import config
from jembe_auth_demo.db import db
from jembe_auth_demo.pages.common import CTable, TableColumn as TC
from jembe_auth_demo.models import User
import sqlalchemy as sa

__all__ = ("CUsers",)


@config(CTable.Config(
    db=db,
    title="Users",
    query=sa.orm.Query(User).order_by(User.first_name),
    columns=[
        TC(User.first_name),
        TC(User.last_name),
        TC(User.email),
    ]
))
class CUsers(CTable):
    pass
