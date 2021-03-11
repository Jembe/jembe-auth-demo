from typing import TYPE_CHECKING, Union
from jembe import Component
from jembe_auth_demo.models import Group

if TYPE_CHECKING:
    from flask import Response


__all__ = ("Groups",)


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
        self.data = Group.query.with_entities(*self.columns).all()
        return super().display()
