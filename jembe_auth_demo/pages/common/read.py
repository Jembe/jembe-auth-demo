from typing import Any, TYPE_CHECKING, Callable, Dict, Iterable, Optional, Tuple, Union

from jembe_auth_demo.common import JembeForm
from jembe_auth_demo.db.exceptions import DBError
from .confirmation import OnConfirmationMixin, Confirmation
from .notifications import Notification
from jembe import Component, action, run_only_once
import sqlalchemy as sa

if TYPE_CHECKING:
    from jembe import ComponentRef, RedisplayFlag, ComponentConfig
    from flask_sqlalchemy import Model, SQLAlchemy
    from flask import Response


__all__ = ("CRead",)


class CRead(Component):
    class Config(Component.Config):
        def __init__(
            self,
            db: "SQLAlchemy",
            model: "Model",
            form: "JembeForm",
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
            self.db = db
            self.model = model
            self.form = form
            self.title = title if title else "View"

            self.default_template = "common/read.html"
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

    _config: Config

    def __init__(self, record_id: int) -> None:
        super().__init__()

    @property
    def title(self) -> str:
        if isinstance(self._config.title, str):
            return self._config.title
        return self._config.title(self)