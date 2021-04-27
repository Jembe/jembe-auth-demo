from typing import (
    Any,
    List,
    TYPE_CHECKING,
    Callable,
    Dict,
    Iterable,
    Optional,
    Tuple,
    Union,
)

from jembe_auth_demo.common import JembeForm
from .link import Link
from .menu import Menu
from .confirmation import OnConfirmationMixin
from jembe import Component

if TYPE_CHECKING:
    from jembe import ComponentRef, RedisplayFlag, ComponentConfig, DisplayResponse
    from flask_sqlalchemy import Model, SQLAlchemy


__all__ = ("CRead",)


class CRead(OnConfirmationMixin,Component):
    class Config(Component.Config):
        def __init__(
            self,
            db: "SQLAlchemy",
            model: "Model",
            form: "JembeForm",
            title: Optional[Union[str, Callable[["Component"], str]]] = None,
            top_menu: Optional[Union[List[Union["Link", "Menu"]], "Menu"]] = None,
            template: Optional[Union[str, Iterable[str]]] = None,
            components: Optional[Dict[str, "ComponentRef"]] = None,
            inject_into_components: Optional[
                Callable[["Component", "ComponentConfig"], dict]
            ] = None,
            redisplay: Tuple["RedisplayFlag", ...] = (),
            changes_url: bool = True,
            url_query_params: Optional[Dict[str, str]] = None,
        ):
            self.db = db
            self.model = model
            self.form = form
            self.title = title if title else "View"

            self.default_template = "common/read.html"
            if template is None:
                template = ("", self.default_template)

            self.top_menu: "Menu" = (
                Menu()
                if top_menu is None
                else (Menu(top_menu) if not isinstance(top_menu, Menu) else top_menu)
            )

            super().__init__(
                template=template,
                components=components,
                inject_into_components=inject_into_components,
                redisplay=redisplay,
                changes_url=changes_url,
                url_query_params=url_query_params,
            )

    _config: Config

    def __init__(self, id: int, _record: Optional["Model"] = None) -> None:
        self._record = _record if _record is not None and _record.id == id else None
        super().__init__()

    @property
    def record(self):
        if self._record is None:
            self._record = self._config.db.session.query(self._config.model).get(
                self.state.id
            )
        return self._record

    @property
    def title(self) -> str:
        if isinstance(self._config.title, str):
            return self._config.title
        return self._config.title(self)

    def display(self) -> "DisplayResponse":
        self.form = self._config.form(obj=self.record, readonly=True).mount(self)
        self.model_info = getattr(self._config.model, "__table_args__", dict()).get(
            "info", dict()
        )
        # initialise menues
        self.top_menu = self._config.top_menu.bind_to(self)
        return super().display()