from jembe_auth_demo.jmb import jmb
from .common import Page, ActionLink
from .dashboard import Dashboard
from .auth import Groups, Users


@jmb.page(
    "main",
    Page.Config(
        page_title="JAD",
        main_menu=[
            ActionLink("/main/dash", "Dashboard"),
            ActionLink("/main/users", "Users"),
            ActionLink("/main/groups", "Groups"),
        ],
        components={
            "dash": Dashboard,
            "users": Users,
            "groups": Groups,
        },
    ),
)
class MainPage(Page):
    pass