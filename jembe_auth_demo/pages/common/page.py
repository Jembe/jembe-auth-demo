from typing import (
    Callable,
    Dict,
    Iterable,
    Sequence,
    TYPE_CHECKING,
    Optional,
    Tuple,
    Union,
    List,
)
from functools import cached_property
from jembe import Component, listener, AccessDenied
from .page_title import PageTitle
from .menu import CMenu
from .confirmation import CConfirmationDialog
from .notifications import CNotifications, CSystemErrorNotification
from .progress_indicator import CProgressIndicator

if TYPE_CHECKING:
    from jembe import Event, RedisplayFlag, ComponentConfig, ComponentRef
    from .link import Link
    from .menu import Menu

__all__ = ("Page", "PageBase")


class PageBase(Component):
    class Config(Component.Config):
        default_template = "common/page_base.html"

        def __init__(
            self,
            page_title: str = "",
            # main_menu: Optional[Union[Sequence[Union["Link", "Menu"]], "Menu"]] = None,
            template: Optional[Union[str, Iterable[str]]] = None,
            components: Optional[Dict[str, "ComponentRef"]] = None,
            inject_into_components: Optional[
                Callable[["Component", "ComponentConfig"], dict]
            ] = None,
            redisplay: Tuple["RedisplayFlag", ...] = (),
            changes_url: bool = True,
            url_query_params: Optional[Dict[str, str]] = None,
        ):
            self.page_title = page_title

            # add default page components
            if components is None:
                components = dict()

            if "_title" not in components:
                components["_title"] = (PageTitle, PageTitle.Config(title=page_title))
            if "_confirmation" not in components:
                components["_confirmation"] = CConfirmationDialog
            if "_notifications" not in components:
                components["_notifications"] = CNotifications
            if "_syserror" not in components:
                components["_syserror"] = CSystemErrorNotification
            if "_progress_indicator" not in components:
                components["_progress_indicator"] = CProgressIndicator

            if template is None:
                template = ("", self.default_template)

            super().__init__(
                template=template,
                components=components,
                inject_into_components=inject_into_components,
                redisplay=redisplay,
                changes_url=changes_url,
                url_query_params=url_query_params,
            )

        @cached_property
        def supported_display_modes(self) -> Tuple[str, ...]:
            return tuple(
                name
                for name in self.components_configs.keys()
                if not name.startswith("_")
            )

    _config: "Config"

    def __init__(self, display_mode: Optional[str] = None):
        if (
            display_mode is None
            or display_mode not in self._config.supported_display_modes
        ):
            try:
                self.state.display_mode = self._config.supported_display_modes[0]
            except IndexError:
                self.state.display_mode = None
        super().__init__()

    @listener(event="_display", source="./*")
    def on_child_display(self, event: "Event"):
        if event.source_name in self._config.supported_display_modes:
            self.state.display_mode = event.source_name

    @listener(event="_exception", source="*")
    def on_child_not_accessible(self, event: "Event"):
        if isinstance(event.exception, AccessDenied):
            try:
                self.state.display_mode = self._config.supported_display_modes[
                    self._config.supported_display_modes.index(event.source_name) + 1
                ]
                event.handled = True
            except (IndexError, ValueError):
                pass


class Page(PageBase):
    class Config(PageBase.Config):
        default_template = "common/page.html"

        def __init__(
            self,
            page_title: str = "",
            main_menu: Optional[Union[Sequence[Union["Link", "Menu"]], "Menu"]] = None,
            template: Optional[Union[str, Iterable[str]]] = None,
            components: Optional[Dict[str, "ComponentRef"]] = None,
            inject_into_components: Optional[
                Callable[["Component", "ComponentConfig"], dict]
            ] = None,
            redisplay: Tuple["RedisplayFlag", ...] = (),
            changes_url: bool = True,
            url_query_params: Optional[Dict[str, str]] = None,
        ):
            if components is None:
                components = dict()

            if "_main_menu" not in components:
                components["_main_menu"] = (
                    CMenu,
                    CMenu.Config(menu=main_menu, template="common/main_menu.html"),
                )
            super().__init__(
                page_title=page_title,
                template=template,
                components=components,
                inject_into_components=inject_into_components,
                redisplay=redisplay,
                changes_url=changes_url,
                url_query_params=url_query_params,
            )
