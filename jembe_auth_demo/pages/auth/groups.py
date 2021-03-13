from jembe import config
from jembe_auth_demo.models import Group
from jembe_auth_demo.db import db
from jembe_auth_demo.pages.common import CTable, TableColumn as TC
import sqlalchemy as sa



__all__ = ("Groups",)


@config(
    CTable.Config(
        # TODO find ways to pickup default db automaticaly
        db=db,
        query=sa.orm.Query(Group),
        # query=sa.orm.Query((Group.id, Group.name, Group.title, Group.description)),
        # query=sa.orm.Query((Group, Group.name)),
        columns=[
            # TC(Group.id),
            TC(Group.name),
            TC(Group.title),
            TC(Group.description),
        ],
    )
)
class Groups(CTable):
    pass
