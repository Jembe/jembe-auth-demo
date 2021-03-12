from typing import TYPE_CHECKING, Union
from jembe import Component
from jembe_auth_demo.models import Group
from jembe_auth_demo.db import db

if TYPE_CHECKING:
    from flask import Response


__all__ = ("Groups",)

# @config(..(query=Query(Group.id, Group.name, Group.description))) 
class Groups(Component):
    # TODO list records
    # order them
    # filter them
    # paginate them
    # select them 
    # execute action on them
    pass
    def display(self) -> Union[str, "Response"]:
        self.columns = [Group.id, Group.name, Group.title, Group.description]
        # self.data = Group.query.with_entities(*self.columns).all()
        self.data = db.session.query(*self.columns).all()
        return super().display()
