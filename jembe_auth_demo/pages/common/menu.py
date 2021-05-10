from typing import (
    Sequence,
    TYPE_CHECKING,
    Optional,
    Union,
    Dict,
    Callable,
    Tuple,
    List,
    Iterable,
    Any,
)
from dataclasses import dataclass, field
from uuid import uuid4

from flask_login import current_user
from jembe import Component
from jembe.component_config import listener


if TYPE_CHECKING:
    from jembe import ComponentConfig, ComponentRef, RedisplayFlag, DisplayResponse
    from flask import Response
    from jembe_auth_demo.pages.common import Link

__all__ = ("CMenu", "Menu")


@dataclass
class Menu:
    items: Sequence[Union["Link", "Menu"]] = field(default_factory=list)
    title: Optional[str] = None
    description: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default="", init=False)

    binded: bool = field(default=False, init=False)

    def __post__init__(self):
        self.id = str(uuid4())

    def bind_to(self, component: "Component") -> "Menu":
        """bind menu to acctual component"""
        binded_menu = Menu(
            title=self.title,
            description=self.description,
            params=self.params,
        )
        binded_menu.id = self.id
        binded_menu.items = [item.bind_to(component) for item in self.items]
        binded_menu.binded = True
        return binded_menu


class CMenu(Component):
    class Config(Component.Config):
        DEFAULT_TEMPLATE = "common/menu.html"

        def __init__(
            self,
            menu: Optional[Union[Sequence[Union["Link", "Menu"]], "Menu"]] = None,
            template: Optional[Union[str, Iterable[str]]] = None,
            components: Optional[Dict[str, "ComponentRef"]] = None,
            inject_into_components: Optional[
                Callable[["Component", "ComponentConfig"], dict]
            ] = None,
            redisplay: Tuple["RedisplayFlag", ...] = (),
            changes_url: bool = False,
            url_query_params: Optional[Dict[str, str]] = None,
        ):
            if template is None:
                template = self.DEFAULT_TEMPLATE

            self.menu: "Menu" = (
                Menu()
                if menu is None
                else (Menu(menu) if not isinstance(menu, Menu) else menu)
            )

            super().__init__(
                template=template,
                components=components,
                inject_into_components=inject_into_components,
                redisplay=redisplay,
                changes_url=changes_url,
                url_query_params=url_query_params,
            )

    @listener(event=["login", "logout"])
    def on_login(self, event):
        return True

    def display(self) -> "DisplayResponse":
        self.menu = self._config.menu.bind_to(self)
        self.is_menu = lambda menu_item: isinstance(menu_item, Menu)
        return super().display()