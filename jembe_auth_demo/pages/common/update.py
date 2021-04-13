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

__all__ = ("CUpdate",)


class CUpdate(OnConfirmationMixin, Component):
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
            self.title = title if title else "Update"

            self.default_template = "common/update.html"
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

    def __init__(
        self,
        id: int,
        form: Optional[JembeForm] = None,
        is_modified: bool = False,
        _record: Optional["Model"] = None,
    ) -> None:
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

    @classmethod
    def load_init_param(cls, config: "ComponentConfig", name: str, value: Any) -> Any:
        if name == "form":
            # otherwise it will use JembeForm.load_init_param
            return config.form.load_init_param(value)
        return super().load_init_param(config, name, value)

    def get_new_record(self) -> "Model":
        return self._config.model()

    @run_only_once
    def mount(self):
        if self.state.form is None:
            self.state.form = self._config.form(obj=self.record)

        if isinstance(self.state.form, JembeForm):
            self.state.form.mount(self)

    @action
    def save(self) -> Optional[bool]:
        self.mount()
        if self.state.form.validate():
            try:
                self.state.form.populate_obj(self.record)
                self._config.db.session.add(self.record)
                self._config.db.session.commit()
                self.emit("save", record=self.record, record_id=self.record.id)
                self.emit(
                    "pushNotification",
                    notification=Notification("{} saved".format(str(self.record))),
                )
                # don't execute display
                return False

            except (sa.exc.SQLAlchemyError, DBError) as error:
                self.emit(
                    "pushNotification",
                    notification=Notification(
                        str(getattr(error, "orig", error))
                        if isinstance(error, sa.exc.SQLAlchemyError)
                        else str(error),
                        "error",
                    ),
                )
        self._config.db.session.rollback()
        return True

    @action
    def cancel(self, confirmed=False):
        if self.state.is_modified and not confirmed:
            self.emit(
                "requestConfirmation",
                confirmation=Confirmation(
                    title="Cancel Update",
                    question="Are you sure, all changes will be lost?",
                    action="cancel",
                    params=dict(confirmed=True),
                ),
            )
        else:
            self.emit("cancel")
            return False

    def display(self) -> Union[str, "Response"]:
        self.mount()
        self.model_info = getattr(self._config.model, "__table_args__", dict()).get(
            "info", dict()
        )
        return super().display()
