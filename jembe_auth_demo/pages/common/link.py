from typing import TYPE_CHECKING, Optional, Union, Callable
from uuid import uuid4
from functools import cached_property, partial
from urllib.parse import urlparse
from jembe.component import component

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
        **kwargs
    ) -> None:
        self._url = url
        self._jrl = jrl
        self._is_accessible = is_accessible
        self._title = title if title is not None else str(uuid4())
        self._description = description

        self.is_for_action = False

    @property
    def url(self) -> Optional[str]:
        if self._url is None:
            return None
        elif isinstance(self._url, str):
            return self._url
        else:
            return self._url(self)

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

    @property
    def description(self) -> Optional[str]:
        if self._description is None:
            return None
        elif isinstance(self._description, str):
            return self._description
        else:
            return self._description(self)


class ActionLink(Link):
    def __init__(
        self,
        component_reference: Union[
            str, Callable[[Optional["Component"]], "ComponentReference"]
        ],
        title: Optional[Union[str, Callable[["Link"], str]]] = None,
        description: Optional[Union[str, Callable[["Link"], str]]] = None,
        **kwargs
    ):
        super().__init__(
            url=lambda self: self.component_reference.url,  # type:ignore
            jrl=lambda self: self.component_reference.jrl,  # type:ignore
            is_accessible=lambda self: self.component_reference.is_accessible(),  # type:ignore
            title=title,
            description=description,
            **kwargs
        )
        self._component:Optional["Component"] = None
        self._component_reference: Callable[
            [Optional["Component"]], "ComponentReference"
        ] = (
            self._str_to_component_reference_lambda(component_reference)
            if isinstance(component_reference, str)
            else component_reference
        )

    def set_component(self, component:"Component"):
        self._component = component

    def _str_to_component_reference_lambda(
        self,
        cstr: str,
    ) -> Callable[[Optional["Component"]], "ComponentReference"]:
        def absolute_component_reference(cr: "ComponentReference", *args, **kwargs):
            return cr

        def relative_component_reference(cstr: str, comp, *args, **kwargs):
            c_names = cstr.split("/")
            cr: "ComponentReference" = comp.component(c_names[0])
            for name in c_names[1:]:
                cr = cr.component(name)
            return cr

        if cstr.startswith("/"):
            # support simple exec name of component like /main/dash etc.
            c_names = cstr.split("/")[1:]
            cr: "ComponentReference" = component("/{}".format(c_names[0]))
            for name in c_names[1:]:
                cr = cr.component(name)
            return partial(absolute_component_reference, cr)
        else:
            return partial(relative_component_reference, cstr)

    @cached_property
    def component_reference(self) -> "ComponentReference":
        if self._component:
            return self._component_reference(self._component)
        return self._component_reference() # type: ignore

    @property
    def exec_name(self) -> str:
        return self.component_reference.exec_name