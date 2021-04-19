from typing import TYPE_CHECKING, Dict, Any
from jembe import config
from jembe.component_config import listener
from jembe_auth_demo.models import Group, User
from jembe_auth_demo.db import db
from jembe_auth_demo.pages.common import (
    CCrudTable,
    TableColumn as TC,
    CCreate,
    CRead,
    CUpdate,
    CDelete,
    ActionLink,
)
import sqlalchemy as sa
from wtforms import StringField, TextAreaField, validators, SelectMultipleField
from jembe_auth_demo.common import JembeForm

if TYPE_CHECKING:
    from jembe import Component, Event


__all__ = ("CGroups",)


class GroupForm(JembeForm):
    name = StringField(
        validators=[
            validators.DataRequired(),
            validators.Length(max=Group.name.type.length),
        ],
    )
    title = StringField(
        validators=[
            validators.DataRequired(),
            validators.Length(max=Group.title.type.length),
        ]
    )
    description = TextAreaField()
    users_ids = SelectMultipleField("Users", coerce=int)

    def mount(self, component: "Component") -> "JembeForm":
        if self.is_readonly:
            self.set_readonly_all()
            self.users_ids.choices = [
                (u.id, "{} {}".format(u.first_name, u.last_name))
                for u in db.session.query(User).filter(User.id.in_(self.users_ids.data))
            ]
        else:
            self.users_ids.choices = [
                (u.id, "{} {}".format(u.first_name, u.last_name))
                for u in db.session.query(User)
            ]
        return super().mount(component)


@config(CCreate.Config(db=db, form=GroupForm, model=Group, title="Add Group"))
class CCreateGroup(CCreate):
    pass


@config(
    CRead.Config(
        db=db,
        form=GroupForm,
        model=Group,
        title=lambda component: "Group: {}".format(component.record.title),
        top_menu=[
            ActionLink(
                lambda self: self.component(  # type:ignore
                    "../update", id=self.record.id, _record=self.record  # type:ignore
                ),
                "Edit",
            ),
            ActionLink("delete", "Delete"),
        ],
        components=dict(delete=(CDelete, CDelete.Config(db=db, model=Group))),
        inject_into_components=lambda self, cconfig: dict(
            id=self.record.id, _record=self.record
        )
        if cconfig.name == "delete"
        else dict(),  # type:ignore
    )
)
class CReadGroup(CRead):
    # def inject_into(self, component: "Component") -> Dict[str, Any]:
    #     from pdb import set_trace; set_trace()
    #     if component._config.name == "delete":
    #         return dict(id=self.record.id, _record=self.record)
    #     return super().inject_into(component)

    @listener(event="delete", source="./*")
    def on_delete(self, event:"Event"):
        self.emit("delete", id=self.state.id)
        return False

@config(
    CUpdate.Config(
        db=db,
        form=GroupForm,
        model=Group,
        title=lambda component: "Group: {}".format(component.record.title),
    )
)
class CUpdateGroup(CUpdate):
    pass


@config(
    CDelete.Config(
        db=db,
        model=Group,
        title=lambda component: 'Delete "{}"?'.format(component.record.title),
    )
)
class CDeleteGroup(CDelete):
    pass


@config(
    CCrudTable.Config(
        db=db,
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
        record_menu=[
            ActionLink(lambda self, record: self.component("read", id=record.id, _record=record), "View"),  # type: ignore
            ActionLink(lambda self, record: self.component("update", id=record.id, _record=record), "Edit"),  # type: ignore
            ActionLink(lambda self, record: self.component("delete", id=record.id, _record=record), "Delete"),  # type: ignore
        ],
        # field_links = {}
        # bulk_menu =[]
        components=dict(
            create=CCreateGroup,
            read=CReadGroup,
            update=CUpdateGroup,
            delete=CDeleteGroup,
        ),
    )
)
class CGroups(CCrudTable):
    pass