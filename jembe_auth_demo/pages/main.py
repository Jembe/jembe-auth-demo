from typing import TYPE_CHECKING, Optional

from jembe import listener
from jembe_auth_demo.jmb import jmb
from .common import Page, ActionLink, PageBase
from .dashboard import Dashboard
from .auth import CGroups, CUsers, CLogin
from flask_login import current_user

if TYPE_CHECKING:
    from jembe import Event


@jmb.page(
    "main",
    Page.Config(
        page_title="JAD",
        main_menu=[
            ActionLink("/main/dash", "Dashboard"),
            ActionLink(
                lambda self: self.component(  # type:ignore
                    "/main/users", display_mode=None
                ),
                "Users",
            ),
            ActionLink(
                lambda self: self.component(  # type:ignore
                    "/main/groups", display_mode=None
                ),
                "Groups",
            ),
        ],
        components={
            "dash": Dashboard,
            "users": CUsers,
            "groups": CGroups,
        },
    ),
)
class MainPage(Page):
    pass


@jmb.page("auth", PageBase.Config(components=dict(login=CLogin)))
class LoginPage(PageBase):
    def __init__(self, display_mode: Optional[str] = None):
        super().__init__(display_mode=display_mode)
        if current_user.is_authenticated:
            self.redirect_to(self.component("/main"))

    @listener(event="login", source="*")
    def on_login(self, event: "Event"):
        self.redirect_to(self.component("/main"))
