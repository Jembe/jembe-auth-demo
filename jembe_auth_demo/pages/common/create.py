from typing import TYPE_CHECKING, Callable, Dict, Iterable, Optional, Tuple, Union
from jembe import Component

if TYPE_CHECKING:
    from jembe import ComponentRef, RedisplayFlag, ComponentConfig

__all__ = ("CCreate",)


class CCreate(Component):
    class Config(Component.Config):
        def __init__(
            self,
            template: Optional[Union[str, Iterable[str]]] = None,
            components: Optional[Dict[str, "ComponentRef"]] = None,
            inject_into_components: Optional[
                Callable[["Component", "ComponentConfig"], dict]
            ] = None,
            redisplay: Tuple["RedisplayFlag", ...] = (),
            changes_url: bool = True,
            url_query_params: Optional[Dict[str, str]] = None,
        ):
            super().__init__(
                template=template,
                components=components,
                inject_into_components=inject_into_components,
                redisplay=redisplay,
                changes_url=changes_url,
                url_query_params=url_query_params,
            )

    _config: Config
