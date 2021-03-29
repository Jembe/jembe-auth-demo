from jembe_auth_demo.common.forms import JembeForm, sa_field
from jembe_auth_demo.pages.common.link import ActionLink
from typing import Optional, TYPE_CHECKING
from jembe import config, listener
from jembe_auth_demo.db import db
from jembe_auth_demo.pages.common import CTable, TableColumn as TC, CCreate
from jembe_auth_demo.models import User
import sqlalchemy as sa

if TYPE_CHECKING:
    from jembe import Event
__all__ = ("CUsers",)


class UserForm(JembeForm):
    first_name = sa_field(User.first_name)
    last_name = sa_field(User.last_name)
    email = sa_field(User.email)
    password = sa_field(User.password)

    active = sa_field(User.active)


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
