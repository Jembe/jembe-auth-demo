from typing import TYPE_CHECKING, List

from jembe import listener
from sqlalchemy.sql.functions import current_user
from jembe_auth_demo.jmb import jmb
from .common import Page, ActionLink
from .dashboard import Dashboard
from .auth import (
    CGroups,
    CUsers,
    CLogin,
    CResetPassword,
    CUserProfile,
    PCLogout,
    CEditUserProfile,
)

if TYPE_CHECKING:
    from jembe import Event
    from .common.link import Link

main_menu: List["Link"] = [
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
    # ActionLink(lambda self: self.component("/main").call("logout"), "Logout"),
    ActionLink("/main/_logout", "Logout", active=True),
    ActionLink("/main/reset_password", "Reset"),
    ActionLink("/main/user_profile", "User profile"),
    ActionLink("/main/login", "Login"),
]


@jmb.page(
    "main",
    Page.Config(
        page_title="JAD",
        main_menu=main_menu,
        components={
            "dash": Dashboard,
            "users": CUsers,
            "groups": CGroups,
            "user_profile": CUserProfile,
            "user_profile_edit": CEditUserProfile,
            "login": CLogin,
            "_logout": PCLogout,
            "reset_password": CResetPassword,
        },
    ),
)
class MainPage(Page):
    @listener(event="logout")
    def on_logout(self, event):
        return True

    @listener(event="login", source="*")
    def on_login(self, event: "Event"):
        # self.redirect_to(self.component("/main"))
        # self.ac_allow("logout")
        self.state.display_mode = "dash"

    @listener(event="save", source="user_profile_edit")
    def on_change_user_profile(self, event: "Event"):
        self.state.display_mode = "user_profile"

    @listener(event="cancel", source="user_profile_edit")
    def on_cancel_user_profile(self, event: "Event"):
        self.state.display_mode = "user_profile"
