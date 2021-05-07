from typing import TYPE_CHECKING, Optional, List

from jembe import listener
from jembe_auth_demo.jmb import jmb
from .common import Page, ActionLink, PageBase
from .dashboard import Dashboard
from .auth import CGroups, CUsers, CLogin, CResetPassword, CUserProfile

if TYPE_CHECKING:
    from jembe import Event
    from .common.link import Link

main_menu:List["Link"] = [
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
        },
    ),
)
class MainPage(Page):
    pass


@jmb.page(
    "auth",
    Page.Config(
        page_title="JAD - Auth",
        main_menu=main_menu,
        components=dict(user=CUserProfile, login=CLogin, reset=CResetPassword),
    ),
)
class AuthPage(Page):
    # def __init__(self, display_mode: Optional[str] = None):
    #     super().__init__(display_mode=display_mode)
    #     if not current_user.is_authenticated:
    #         self.redirect_to(self.component("/main"))

    @listener(event="login", source="*")
    def on_login(self, event: "Event"):
        self.redirect_to(self.component("/main"))

    # @action
    # def logout(self):
    #     pass

    def display(self):
        if self.state.display_mode == "login":
            return self.render_template(self._config.super.default_template)
        return self.render_template(self._config.template)
