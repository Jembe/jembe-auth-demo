from jembe_auth_demo.pages.common.link import ActionLink
from typing import TYPE_CHECKING, Optional
from jembe import config, listener
from jembe_auth_demo.models import Group
from jembe_auth_demo.db import db
from jembe_auth_demo.pages.common import CTable, TableColumn as TC, CCreate, ActionLink
import sqlalchemy as sa
from wtforms_sqlalchemy.orm import model_form
from jembe_auth_demo.common import JembeForm

if TYPE_CHECKING:
    from jembe import Event


__all__ = ("CGroups",)

GroupForm = model_form(
    Group,
    db,
    base_class=JembeForm,
    exclude=["users"]
)


@config(CCreate.Config(db=db, form=GroupForm, model=Group))
class CCreateGroup(CCreate):
    pass


@config(
    CTable.Config(
        db=db,  # TODO find ways to pickup default db automaticaly
        title="Groups",
        query=sa.orm.Query(Group).order_by(Group.id),
        columns=[
            TC(Group.name),  # TODO add action
            TC(Group.title),
            TC(Group.description),
        ],
        default_filter=lambda value: Group.title.ilike("%{}%".format(value)),
        top_menu=[
            ActionLink("create", "Add"),
        ],
        # record_menu = [
        #   CAction(lambda self, record: self.component('edit',id=record.id), "Edit", icon)
        #   CAction(lambda self, record: self.component('view',id=record.id) if not self.component('edit', id=record.id).is_accessile() else None, "View", icon)
        # ]
        # field_links = {}
        # bulk_menu =[]
        components=dict(create=CCreateGroup),
    )
)
class CGroups(CTable):
    def __init__(
        self,
        order_by: int = 0,
        page: int = 0,
        page_size: int = 10,
        search_query: Optional[str] = None,
        display_mode: Optional[str] = None,
    ):
        if (
            display_mode is not None
            and display_mode not in self._config.components.keys()
        ):
            self.state.display_mode = None

        super().__init__(
            order_by=order_by, page=page, page_size=page_size, search_query=search_query
        )

    @listener(event="_display", source="./create")
    def on_child_display(self, event: "Event"):
        self.state.display_mode = event.source_name

    @listener(event="cancel", source="./create")
    def on_child_cancel(self, event: "Event"):
        self.state.display_mode = None
