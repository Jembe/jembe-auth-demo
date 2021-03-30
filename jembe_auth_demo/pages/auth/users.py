from jembe_auth_demo.common.forms import JembeForm
from jembe_auth_demo.pages.common.link import ActionLink
from typing import Optional, TYPE_CHECKING
from jembe import config, listener
from jembe_auth_demo.db import db
from jembe_auth_demo.pages.common import CTable, TableColumn as TC, CCreate
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
    from jembe import Event, Component
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
        self.groups_ids.choices = [
            (g.id, g.title) for g in db.session.query(Group)[:100]
        ]
        return super().mount(component)


@config(
    CTable.Config(
        db=db,
        title="Users",
        query=sa.orm.Query(User).order_by(User.first_name),
        columns=[
            TC(User.first_name),
            TC(User.last_name),
            TC(User.email),
        ],
        top_menu=[ActionLink("create", "Add")],
        components=dict(
            create=(
                CCreate,
                CCreate.Config(db=db, model=User, form=UserForm, title="Add User"),
            )
        ),
    )
)
class CUsers(CTable):
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

    @listener(event=["save", "cancel"], source="./create")
    def on_child_finish(self, event: "Event"):
        self.state.display_mode = None
