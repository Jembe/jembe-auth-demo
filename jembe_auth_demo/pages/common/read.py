from jembe_auth_demo.pages.common.delete import action_delete_record
from typing import (
    TYPE_CHECKING,
    List,
    Callable,
    Dict,
    Iterable,
    Optional,
    Tuple,
    Union,
)

from jembe import action

from .menu import Menu
from .form import CFormBase

if TYPE_CHECKING:
    from jembe_auth_demo.common import JembeForm
    from jembe import (
        Component,
        ComponentRef,
        RedisplayFlag,
        ComponentConfig,
        DisplayResponse,
    )
    from flask_sqlalchemy import Model, SQLAlchemy
    from .link import Link


__all__ = ("CRead", "CReadWithDelete")


class CRead(CFormBase):
    class Config(CFormBase.Config):
        default_title = "View"
        default_template = "common/read.html"

        def __init__(
            self,
            db: "SQLAlchemy",
            form: "JembeForm",
            model: "Model",
            top_menu: Optional[Union[List[Union["Link", "Menu"]], "Menu"]] = None,
            title: Optional[Union[str, Callable[["Component"], str]]] = None,
            template: Optional[Union[str, Iterable[str]]] = None,
            components: Optional[Dict[str, "ComponentRef"]] = None,
            inject_into_components: Optional[
                Callable[["Component", "ComponentConfig"], dict]
            ] = None,
            redisplay: Tuple["RedisplayFlag", ...] = (),
            changes_url: bool = True,
            url_query_params: Optional[Dict[str, str]] = None,
        ):
            self.model = model
            self.top_menu: "Menu" = (
                Menu()
                if top_menu is None
                else (Menu(top_menu) if not isinstance(top_menu, Menu) else top_menu)
            )
            super().__init__(
                db,
                form,
                title=title,
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

    def display(self) -> "DisplayResponse":
        self.form = self._config.form(obj=self.record, readonly=True).mount(self)
        self.model_info = getattr(self._config.model, "__table_args__", dict()).get(
            "info", dict()
        )
        # initialise menues
        self.top_menu = self._config.top_menu.bind_to(self)
        return super().display()


class CReadWithDelete(CRead):
    @action
    def delete_record(self, confirmed:bool=False):
        action_delete_record(
            component=self,
            action_name="delete_record",
            action_params=dict(confirmed=True),
            confirmed=confirmed,
            db=self._config.db,
            model=self._config.model,
            id=self.record.id,
            record=self.record
        )