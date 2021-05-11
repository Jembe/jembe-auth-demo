from typing import TYPE_CHECKING, Optional, Union, Callable, Dict, Any
from copy import copy
from uuid import uuid4
from functools import cached_property, partial
from urllib.parse import urlparse
from jembe.component import component
from jembe.component_config import ComponentConfig

if TYPE_CHECKING:
    from jembe import Component, ComponentReference
__all__ = ("ActionLink", "Link")


class Link:
    def __init__(
        self,
        url: Optional[Union[str, Callable[["Link"], str]]] = None,
        jrl: Optional[Union[str, Callable[["Link"], str]]] = None,
        is_accessible: Union[bool, Callable[["Link"], bool]] = True,
        title: Optional[Union[str, Callable[["Link"], str]]] = None,
        description: Optional[Union[str, Callable[["Link"], str]]] = None,
        **params
    ) -> None:
        self._url = url
        self._jrl = jrl
        self._is_accessible = is_accessible
        self._title = title if title is not None else str(uuid4())
        self._description = description
        self.params = params
        self.callable_params: Dict[str, Any] = dict()

        self.is_action_link = False

        self.from_component: Optional["Component"] = None
        self.binded = False

    def bind_to(self, component: "Component") -> "Link":
        binded_link = copy(self)
        binded_link.from_component = component
        binded_link.binded = True
        return binded_link

    @property
    def url(self) -> Optional[str]:
        if self._url is None:
            return None
        elif isinstance(self._url, str):
            return self._url
        else:
            return self._url(self, **self.callable_params)  # type:ignore

    @property
    def pathname(self) -> Optional[str]:
        return str(urlparse(self.url).path)

    @property
    def jrl(self) -> Optional[str]:
        if self._jrl is None:
            return None
        elif isinstance(self._jrl, str):
            return self._jrl
        else:
            return self._jrl(self, **self.callable_params)  # type:ignore

    @property
    def is_accessible(self) -> bool:
        if isinstance(self._is_accessible, bool):
            return self._is_accessible
        else:
            return self._is_accessible(self, **self.callable_params)  # type:ignore

    @property
    def title(self) -> str:
        if isinstance(self._title, str):
            return self._title
        else:
            return self._title(self, **self.callable_params)  # type:ignore

    @property
    def description(self) -> Optional[str]:
        if self._description is None:
            return None
        elif isinstance(self._description, str):
            return self._description
        else:
            return self._description(self, **self.callable_params)  # type:ignore

    def set(self, **kwargs) -> "Link":
        """Add additional paramas for callables and resets previous ones"""
        # setting additional params can change action output
        link = copy(self)
        link.callable_params = dict()
        for k, v in kwargs.items():
            link.callable_params[k] = v
        return link

    @property
    def is_link_to_action(self) -> bool:
        return False


class ActionLink(Link):
    def __init__(
        self,
        to_component: Union[
            str, Callable[[Optional["Component"]], "ComponentReference"]
        ],
        title: Optional[Union[str, Callable[["Link"], str]]] = None,
        description: Optional[Union[str, Callable[["Link"], str]]] = None,
        **params
    ):
        super().__init__(
            url=self._get_url_,  # type:ignore
            jrl=self._get_jrl_,  # type:ignore
            is_accessible=self._is_accessible_,  # type:ignore
            title=title,
            description=description,
            **params
        )
        self._to_component = to_component
        self.is_action_link = True

    def _get_url_(self, link: "ActionLink", *args, **kwargs) -> str:
        return link.to_component_reference.url

    def _get_jrl_(self, link: "ActionLink", *args, **kwargs) -> str:
        return link.to_component_reference.jrl

    def _is_accessible_(self, link: "ActionLink", *args, **kwargs) -> bool:
        return link.to_component_reference.is_accessible

    def _str_to_component_reference_lambda(
        self, cstr: str
    ) -> Callable[[Optional["Component"]], "ComponentReference"]:
        def absolute_component_reference(cstr: str, *args, **kwargs):
            # support simple exec name of component like /main/dash etc.
            c_names = cstr.split("/")[1:]
            do_reset_params = len(c_names) == 1
            cr: "ComponentReference" = component(
                "/{}".format(c_names[0]), do_reset_params
            )
            for index, name in enumerate(c_names[1:]):
                if index == len(c_names) - 2:
                    cr = cr.component_reset(name)
                else:
                    cr = cr.component(name)
            cr.kwargs = self.params.copy()
            return cr

        def relative_component_reference(cstr: str, comp: "Component", *args, **kwargs):
            c_names = cstr.split("/")
            cr: "ComponentReference" = (
                comp.component(c_names[0])
                if not c_names[0].endswith("()")
                else comp.component().call(c_names[0][:-2])
            )
            for name in c_names[1:]:
                cr = cr.component(name)
            cr.kwargs = self.params.copy()
            return cr

        if cstr.startswith("/"):
            return partial(absolute_component_reference, cstr)
        else:
            return partial(relative_component_reference, cstr, self.from_component)

    @cached_property
    def to_component_reference(self) -> "ComponentReference":
        to_component: Callable[[Optional["Component"]], "ComponentReference"] = (
            self._str_to_component_reference_lambda(self._to_component)
            if isinstance(self._to_component, str)
            else self._to_component
        )
        if self.from_component:
            return to_component(self.from_component, **self.callable_params)  # type: ignore
        return to_component()  # type: ignore

    @property
    def exec_name(self) -> str:
        return self.to_component_reference.exec_name

    @property
    def is_link_to_action(self) -> bool:
        return (
            self.to_component_reference.action != ComponentConfig.DEFAULT_DISPLAY_ACTION
        )
