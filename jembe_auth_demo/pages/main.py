from jembe_auth_demo.jmb import jmb
from .common import Page, ActionLink
from .dashboard import Dashboard
from .auth import CGroups, CUsers


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