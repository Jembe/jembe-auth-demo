from typing import TYPE_CHECKING, Optional, Union, Iterable, Dict, Callable, Tuple
from functools import cached_property
from uuid import uuid4
from jembe import Component
from jembe.component import component

if TYPE_CHECKING:
    from jembe import (
        ComponentConfig,
        ComponentRef,
        CConfigRedisplayFlag,
        ComponentRenderer,
    )

__all__ = ("Menu", "MenuItem")


class MenuItem:
    def __init__(
        self,
        url: Optional[Union[str, Callable[["MenuItem"], str]]] = None,
        jrl: Optional[Union[str, Callable[["MenuItem"], str]]] = None,
        is_accessible: Union[bool, Callable[["MenuItem"], bool]] = True,
        title: Optional[Union[str, Callable[["MenuItem"], str]]] = None,
        *items: "MenuItem"
    ) -> None:
        self._url = url
        self._jrl = jrl
        self._is_accessible = is_accessible
        self._title = title if title is not None else str(uuid4())

        self.items = items
        self.is_group = len(items) > 0

        self._component: Optional[str] = None

    @property
    def url(self) -> Optional[str]:
        if self._url is None:
            return None
        elif isinstance(self._url, str):
            return self._url
        else:
            return self._url(self)

    @property
    def jrl(self) -> Optional[str]:
        if self._jrl is None:
            return None
        elif isinstance(self._jrl, str):
            return self._jrl
        else:
            return self._jrl(self)

    @property
    def is_accessible(self) -> bool:
        if isinstance(self._is_accessible, bool):
            return self._is_accessible
        else:
            return self._is_accessible(self)

    @property
    def title(self) -> str:
        if isinstance(self._title, str):
            return self._title
        else:
            return self._title(self)

    @classmethod
    def for_component(
        cls,
        component: str,
        title: Optional[str] = None,
    ) -> "MenuItem":
        mi = MenuItem(
            url=lambda self: self._component_renderer.url,
            jrl=lambda self: self._component_renderer.jrl,
            is_accessible=lambda self: self._component_renderer.is_accessible(),
            title=title,
        )
        mi._component = component
        return mi

    @cached_property
    def _component_renderer(self) -> "ComponentRenderer":
        if self._component is None:
            return ValueError()
        if self._component.startswith("/"):
            # support simple exec name of component like /main/dash etc.
            c_names = self._component.split("/")[1:]
            cr: "ComponentRenderer" = component("/{}".format(c_names[0]))
            for name in c_names[1:]:
                cr = cr.component(name)
            return cr
        else:
            raise NotImplementedError()

    @property
    def exec_name(self) -> Optional[str]:
        if self._component is None:
            return None
        return self._component_renderer.exec_name


class Menu(Component):
    class Config(Component.Config):
        DEFAULT_TEMPLATE = "common/menu.html"

        def __init__(
            self,
            items: Optional[Iterable["MenuItem"]] = None,
            template: Optional[Union[str, Iterable[str]]] = None,
            components: Optional[Dict[str, "ComponentRef"]] = None,
            inject_into_components: Optional[
                Callable[["Component", "ComponentConfig"], dict]
            ] = None,
            redisplay: Tuple["CConfigRedisplayFlag", ...] = (),
            changes_url: bool = False,
            url_query_params: Optional[Dict[str, str]] = None,
        ):
            if template is None:
                template = self.DEFAULT_TEMPLATE

            self.items = tuple() if items is None else items

            super().__init__(
                template=template,
                components=components,
                inject_into_components=inject_into_components,
                redisplay=redisplay,
                changes_url=changes_url,
                url_query_params=url_query_params,
            )
