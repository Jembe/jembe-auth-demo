from typing import  TYPE_CHECKING

from jembe import listener
from jembe.processor import EmitCommand
from jembe_auth_demo.jmb import jmb
from .common import Page, ActionLink, PageBase
from .dashboard import Dashboard
from .auth import CGroups, CUsers, CLogin
from flask_login import current_user
from jembe.app import get_processor

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
    # def __init__(self, display_mode: Optional[str] = None):
    #     super().__init__(display_mode=display_mode)
    #     if current_user.is_authenticated:
    #         # # print(current_user)
    #         # TODO add remove component from processing with self.remove() or self.remove(relative_exec_name)
    #         self.component("/main")()
    #         self.remove()

    @listener(event="login", source="*")
    def on_login(self, event: "Event"):
        self.component("/main")()
        self.remove()
        return False

    def remove(self):
        processor = get_processor()
        processor._commands = [
            c
            for c in processor._commands
            if not c.component_exec_name.startswith(self.exec_name)
            or isinstance(c, EmitCommand)
        ]
        processor.renderers = {
            k: r
            for k, r in processor.renderers.items()
            if not k.startswith(self.exec_name)
        }
        processor.components = {
            k: c
            for k, c in processor.components.items()
            if not k.startswith(self.exec_name)
        }

    # def display(self):
    #     if current_user.is_authenticated:
    #         # # print(current_user)
    #         self.component("/main")()
    #         return ""
    #         # return None
    #         # return redirect("/")
    #     return super().display()