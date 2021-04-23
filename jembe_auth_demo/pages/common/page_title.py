from typing import Callable, Dict, Iterable, TYPE_CHECKING, Optional, Tuple, Union
from jembe import Component, config, listener

if TYPE_CHECKING:
    from jembe import RedisplayFlag, ComponentConfig, ComponentRef, Event

__all__ = ("PageTitle",)


@config(Component.Config(template="common/page_title.html", changes_url=False))
class PageTitle(Component):
    class Config(Component.Config):
        def __init__(
            self,
            title: str = "",
            template: Optional[Union[str, Iterable[str]]] = None,
            components: Optional[Dict[str, "ComponentRef"]] = None,
            inject_into_components: Optional[
                Callable[["Component", "ComponentConfig"], dict]
            ] = None,
            redisplay: Tuple["RedisplayFlag", ...] = (),
            changes_url: bool = True,
            url_query_params: Optional[Dict[str, str]] = None,
        ):
            self.title = title
            super().__init__(
                template=template,
                components=components,
                inject_into_components=inject_into_components,
                redisplay=redisplay,
                changes_url=changes_url,
                url_query_params=url_query_params,
            )

    def __init__(self, title: str = ""):
        if title == "":
            self.state.title = self._config.title
        super().__init__()

    @listener(event="setPageTitle")
    def on_set_page_title(self, event: "Event"):
        if "title" in event.params and event.params["title"]:
            self.state.title = event.params["title"]
        else:
            self.state.title = self._config.title
