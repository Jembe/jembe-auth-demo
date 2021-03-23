from typing import Any, TYPE_CHECKING, Callable, Dict, Iterable, Optional, Tuple, Union
from jembe_auth_demo.common import JembeForm
from .confirmation import OnConfirmationMixin, Confirmation
from jembe import Component, action, run_only_once
import sqlalchemy as sa

if TYPE_CHECKING:
    from jembe import ComponentRef, RedisplayFlag, ComponentConfig
    from flask_sqlalchemy import Model, SQLAlchemy
    from flask import Response

__all__ = ("CCreate",)


class CCreate(OnConfirmationMixin, Component):
    class Config(Component.Config):
        def __init__(
            self,
            db: "SQLAlchemy",
            model: "Model",
            form: "JembeForm",
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

            self.default_template = "common/create.html"
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

    def __init__(self, form: Optional[JembeForm] = None) -> None:
        super().__init__()

    @classmethod
    def load_init_param(cls, config: "ComponentConfig", name: str, value: Any) -> Any:
        if name == "form":
            # otherwise it will use JembeForm.load_init_param
            return config.form.load_init_param(value)
        return super().load_init_param(name, value)

    def get_new_record(self) -> "Model":
        return self._config.model()

    @run_only_once
    def mount(self):
        if self.state.form is None:
            self.state.form = self._config.form(obj=self.get_new_record())

    @action
    def save(self) -> Optional[bool]:
        self.mount()
        if self.state.form.validate():
            try:
                record = self.get_new_record()
                self.state.form.populate_obj(record)
                self._config.db.session.add(record)
                self._config.db.session.commit()
                self.emit("save", record=record, record_id=record.id)
                # self.emit(
                #     "pushNotification",
                #     notification=Notification("{} saved".format(str(record))),
                # )
                # don't execute display
                return False
            except sa.exc.SQLAlchemyError as sql_error:
                # self.emit(
                #     "pushNotification",
                #     notification=Notification(
                #         str(getattr(sql_error, "orig", sql_error)), "error"
                #     ),
                # )
                return True
        return None

    @action
    def cancel(self, confirmed=False):
        if self._is_record_modified() and not confirmed:
            self.emit(
                "requestConfirmation",
                confirmation=Confirmation(
                    title="Cancel Add",
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

    def _is_record_modified(self) -> bool:
        self.mount()
        new_record = self.get_new_record()
        self.state.form.populate_obj(new_record)
        empty_record = self.get_new_record()
        for column_name in new_record.__table__.columns.keys():
            if getattr(new_record, column_name) != getattr(empty_record, column_name):
                return True
        return False
