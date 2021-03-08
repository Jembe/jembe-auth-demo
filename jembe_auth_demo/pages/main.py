from jembe_auth_demo.jmb import jmb
from .common import Page
from .dashboard import Dashboard
from .auth import Groups, Users


@jmb.page(
    "main",
    Page.Config(
        page_title="JAD",
        components={
            "dash": Dashboard,
            "users": Users,
            "groups": Groups,
        },
    ),
)
class MainPage(Page):
    pass