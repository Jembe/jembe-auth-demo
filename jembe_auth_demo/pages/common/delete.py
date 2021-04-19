from typing import TYPE_CHECKING, Callable, Dict, Iterable, Optional, Tuple, Union

from .confirmation import OnConfirmationMixin, Confirmation
from .notifications import Notification
from jembe import Component, action
import sqlalchemy as sa

if TYPE_CHECKING:
    from jembe import ComponentRef, RedisplayFlag, ComponentConfig
    from flask_sqlalchemy import Model, SQLAlchemy
    from flask import Response

__all__ = ("CDelete",)


class CDelete(OnConfirmationMixin, Component):
    class Config(Component.Config):
        def __init__(
            self,
            db: "SQLAlchemy",
            model: "Model",
            title: Optional[Union[str, Callable[["Component"], str]]] = None,
            template: Optional[Union[str, Iterable[str]]] = None,
            components: Optional[Dict[str, "ComponentRef"]] = None,
            inject_into_components: Optional[
                Callable[["Component", "ComponentConfig"], dict]
            ] = None,
            redisplay: Tuple["RedisplayFlag", ...] = (),
            changes_url: bool = False,
            url_query_params: Optional[Dict[str, str]] = None,
        ):
            self.db = db
            self.model = model
            self.title = title if title else "Delete"

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

    @action
    def delete_record(self, confirmed=False):
        if not confirmed:
            self.request_confirmation()
        else:
            try:
                self._config.db.session.delete(self.record)
                self._config.db.session.commit()
                self.emit("delete", record=self.record, id=self.record.id)
                self.emit(
                    "pushNotification",
                    notification=Notification("{} deleted".format(str(self.record))),
                )
            except sa.exc.SQLAlchemyError as error:
                self._config.db.session.rollback()
                self.emit(
                    "pushNotification",
                    notification=Notification(
                        str(getattr(error, "orig", error)), "error"
                    ),
                )
        return False

    def display(self) -> Union[str, "Response"]:
        self.request_confirmation()
        return self.render_template_string("")

    def request_confirmation(self):
        self.emit(
            "requestConfirmation",
            confirmation=Confirmation(
                title=self.title,
                question="Are you sure you want to delete this record?",
                action="delete_record",
                params=dict(confirmed=True),
                state=dict(id=self.state.id),
                force_init=True,
            ),
        )

    @property
    def title(self) -> str:
        if isinstance(self._config.title, str):
            return self._config.title
        return self._config.title(self)
