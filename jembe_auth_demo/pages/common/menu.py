from typing import (
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

from jembe import Component


if TYPE_CHECKING:
    from jembe import (
        ComponentConfig,
        ComponentRef,
        RedisplayFlag,
    )
    from flask import Response
    from jembe_auth_demo.pages.common import Link

__all__ = ("CMenu", "Menu")


@dataclass
class Menu:
    items: List[Union["Link", "Menu"]] = field(default_factory=list)
    title: Optional[str] = None
    description: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default="", init=False)
    jmb_parent_menues_ids: List[str] = field(init=False, default_factory=list)

    def __post__init__(self):
        self.id = str(uuid4())

    def mount(self):
        """associtate parent_menu_ids to all menu items"""
        for item in self.items:
            if isinstance(item, Menu):
                item.jmb_parent_menues_ids.extend(self.jmb_parent_menues_ids)
                item.mount()
            else:
                item.jmb_parent_menues_ids = self.jmb_parent_menues_ids


class CMenu(Component):
    class Config(Component.Config):
        DEFAULT_TEMPLATE = "common/menu.html"

        def __init__(
            self,
            menu: Optional[Union[List[Union["Link", "Menu"]], "Menu"]] = None,
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
            self.menu.mount()

            super().__init__(
                template=template,
                components=components,
                inject_into_components=inject_into_components,
                redisplay=redisplay,
                changes_url=changes_url,
                url_query_params=url_query_params,
            )

    def display(self) -> Union[str, "Response"]:
        self.is_menu = lambda menu_item: isinstance(menu_item, Menu)
        return super().display()