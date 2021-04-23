from typing import TYPE_CHECKING
from jembe_auth_demo.common.forms import JembeForm
from jembe import config, listener
from jembe_auth_demo.db import db
from jembe_auth_demo.pages.common import (
    CCrudTable,
    TableColumn as TC,
    CCreate,
    ActionLink,
    CRead,
    CUpdate,
    CDelete,
)
from jembe_auth_demo.models import User, Group
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SelectMultipleField,
    validators,
)
from wtforms.fields.html5 import EmailField
import sqlalchemy as sa

if TYPE_CHECKING:
    from jembe import Component
    from flask_sqlalchemy import Model
    from sqlalchemy.orm.session import Session

__all__ = ("CUsers",)


class UserForm(JembeForm):
    first_name = StringField(
        validators=[
            validators.DataRequired(),
            validators.Length(max=User.first_name.type.length),
        ]
    )
    last_name = StringField(
        validators=[
            validators.DataRequired(),
            validators.Length(max=User.last_name.type.length),
        ]
    )
    email = EmailField(
        validators=[
            validators.DataRequired(),
            validators.Email(),
            validators.Length(max=User.email.type.length),
        ]
    )
    active = BooleanField(default=True)
    groups_ids = SelectMultipleField(coerce=int)

    def mount(self, component: "Component"):
        if self.is_readonly:
            self.set_readonly_all()
            self.groups_ids.choices = [
                (g.id, g.title)
                for g in db.session.query(Group).filter(
                    Group.id.in_(self.groups_ids.data)
                )[:100]
            ]
        else:
            self.groups_ids.choices = [
                (g.id, g.title) for g in db.session.query(Group)[:100]
            ]
        return super().mount(component)


class CreateUserForm(UserForm):
    password = PasswordField(
        validators=[
            validators.DataRequired(),
            validators.Length(
                min=7, max=User.password.type.length, message="Select stronger password"
            ),
        ]
    )
    confirm_password = PasswordField(
        validators=[validators.EqualTo("password", message="Passwords must match")]
    )
    def submit(self, session: "Session", record: "User", **kwargs):
        super().submit(session, record, **kwargs)
        record.set_password(self.password.data)


class UpdateUserForm(UserForm):
    new_password = PasswordField()
    confirm_password = PasswordField(
        validators=[validators.EqualTo("new_password", message="Passwords must match")]
    )
    def submit(self, session: "Session", record: "User", **kwargs):
        super().submit(session, record, **kwargs)
        if self.new_password.data != "":
            record.set_password(self.new_password.data)


@config(
    CCrudTable.Config(
        db=db,
        title="Users",
        query=sa.orm.Query(User).order_by(User.first_name),
        columns=[
            TC(User.first_name),
            TC(User.last_name),
            TC(User.email),
        ],
        components=dict(
            create=(
                CCreate,
                CCreate.Config(
                    db=db, model=User, form=CreateUserForm, title="Add User"
                ),
            ),
            read=(
                CRead,
                CRead.Config(
                    db=db,
                    model=User,
                    form=UserForm,
                    top_menu=[
                        ActionLink(
                            lambda self: self.component(  # type:ignore
                                "../update",
                                id=self.record.id,  # type:ignore
                                _record=self.record,  # type:ignore
                            ),
                            "Edit",
                        ),
                        ActionLink("delete", "Delete"),
                    ],
                    components={"delete": (CDelete, CDelete.Config(db=db, model=User))},
                    inject_into_components=lambda self, cconfig: dict(
                        id=self.record.id, _record=self.record
                    )
                    if cconfig.name in ("delete",)
                    else dict(),
                ),
            ),
            update=(CUpdate, CUpdate.Config(db=db, model=User, form=UpdateUserForm)),
            delete=(CDelete, CDelete.Config(db=db, model=User)),
        ),
        top_menu=[ActionLink("create", "Add")],
        record_menu=[
            ActionLink(
                lambda self, record: self.component(  # type:ignore
                    "read", id=record.id, _record=record
                ),
                "View",
            ),
            ActionLink(
                lambda self, record: self.component(  # type:ignore
                    "update", id=record.id, _record=record
                ),
                "Edit",
            ),
            ActionLink(
                lambda self, record: self.component(  # type:ignore
                    "delete", id=record.id, _record=record
                ),
                "Delete",
            ),
        ],
    )
)
class CUsers(CCrudTable):
    @listener(event="delete", source="read/delete")
    def on_delete(self, event):
        self.state.display_mode = None