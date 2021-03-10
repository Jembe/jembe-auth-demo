from jembe_auth_demo.jmb import jmb
from .common import Page, MenuItem
from .dashboard import Dashboard
from .auth import Groups, Users


@jmb.page(
    "main",
    Page.Config(
        page_title="JAD",
        main_menu_items=[
            MenuItem.for_component("/main/dash", "Dashboard"),
            MenuItem.for_component("/main/users", "Users"),
            MenuItem.for_component("/main/groups", "Groups"),
            MenuItem("/main/test", "$jmb.component('/main').component('test')", title="Test")
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