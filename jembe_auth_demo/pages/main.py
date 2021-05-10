from typing import TYPE_CHECKING, Optional, List

from jembe import listener, action
from jembe_auth_demo.jmb import jmb
from flask_login import logout_user, current_user
from .common import Page, ActionLink, PageBase
from .dashboard import Dashboard
from .auth import CGroups, CUsers, CLogin, CResetPassword, CUserProfile, CLogout

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
            "login": CLogin,
            "_logout": CLogout,
            "reset_password": CResetPassword,
        },
    ),
)
class MainPage(Page):
    # def init(self):
    #     if not current_user.is_authenticated:
    #         self.ac_deny("logout")
    #     return super().init()

    # @action
    # def logout(self):
    #     logout_user()
    #     self.ac_deny("logout")
    #     self.emit("logout")
    #     self.state.display_mode = "dash"

    @listener(event="logout")
    def on_logout(self, event):
        self.state.display_mode = "dash"

    @listener(event="login", source="*")
    def on_login(self, event: "Event"):
        # self.redirect_to(self.component("/main"))
        # self.ac_allow("logout")
        self.state.display_mode = "dash"

    def display(self):
        if self.state.display_mode == "login":
            return self.render_template(self._config.super.default_template)
        return self.render_template(self._config.template)


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
    def init(self):
        if not current_user.is_authenticated:
            self.ac_deny("logout")
        return super().init()

    # @listener(event="login", source="*")
    # def on_login(self, event: "Event"):
    #     self.redirect_to(self.component("/main"))

    @action
    def logout(self):
        logout_user()
        return True

    def display(self):
        if self.state.display_mode == "login":
            return self.render_template(self._config.super.default_template)
        return self.render_template(self._config.template)
