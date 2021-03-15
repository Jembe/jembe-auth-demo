from jembe import config
from jembe_auth_demo.models import Group
from jembe_auth_demo.db import db
from jembe_auth_demo.pages.common import CTable, TableColumn as TC
import sqlalchemy as sa


__all__ = ("Groups",)

@config(
    CTable.Config(
        db=db,  # TODO find ways to pickup default db automaticaly
        query=sa.orm.Query(Group).order_by(Group.id),
        columns=[
            TC(Group.name), # TODO add action
            TC(Group.title),
            TC(Group.description),
        ],
        default_filter=lambda value: Group.title.ilike("%{}%".format(value))
        # filters=[
        #   ChoiceFilter(Group.name.... whatever, "Title")
        #   ChoiceFilterGroup(lambda value:Group.name.... whatever, values, titles)
        #   FieldFilter(Group.name, optial operators ...)
        # ]
        # actions = [
        #   CAction(lambda self: self.component('create'), "Create", icon) # Action and MenuItem are the same thing
        # ]
        # record_actions = [
        #   CAction(lambda self, record: self.component('edit',id=record.id), "Edit", icon) 
        #   CAction(lambda self, record: self.component('view',id=record.id) if not self.component('edit', id=record.id).is_accessile() else None, "View", icon) 
        # ]
        # bulk_actions =[]
    )
)
class Groups(CTable):
    pass
