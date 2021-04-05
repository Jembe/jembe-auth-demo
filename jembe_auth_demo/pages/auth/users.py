from jembe_auth_demo.common.forms import JembeForm
from typing import TYPE_CHECKING
from jembe import config
from jembe_auth_demo.db import db
from jembe_auth_demo.pages.common import (
    CCrudTable,
    TableColumn as TC,
    CCreate,
    ActionLink,
    CRead,
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
    password = PasswordField(
        validators=[
            validators.DataRequired(),
            validators.Length(max=User.password.type.length),
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
                CCreate.Config(db=db, model=User, form=UserForm, title="Add User"),
            ),
            read=(CRead, CRead.Config(db=db, model=User, form=UserForm)),
        ),
        top_menu=[ActionLink("create", "Add")],
        record_menu=[
            ActionLink(
                lambda self, record: self.component(  # type:ignore
                    "read", id=record.id, _record=record
                ),
                "View",
            )
        ],
    )
)
class CUsers(CCrudTable):
    pass