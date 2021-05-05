from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, Dict, Iterable, Optional, Tuple, Union, Any
from jembe import Component, run_only_once
import sqlalchemy as sa
from jembe_auth_demo.common import JembeForm
from .confirmation import OnConfirmationMixin
from .notifications import Notification

if TYPE_CHECKING:
    from jembe import ComponentRef, RedisplayFlag, ComponentConfig, DisplayResponse
    from flask_sqlalchemy import SQLAlchemy, Model
    from sqlalchemy.orm.scoping import scoped_session

__all__ = (
    "CFormBase",
    "CForm",
)


class CFormBase(OnConfirmationMixin, Component):
    class Config(Component.Config):
        default_template = "common/form.html"
        default_title = "Form"

        def __init__(
            self,
            db: "SQLAlchemy",
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
            self.form = form
            self.title = title if title else self.default_title

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

    @property
    def title(self) -> str:
        if isinstance(self._config.title, str):
            return self._config.title
        return self._config.title(self)

    @property
    def session(self) -> "scoped_session":
        return self._config.db.session

    @classmethod
    def load_init_param(cls, config: "ComponentConfig", name: str, value: Any) -> Any:
        if name == "form":
            # otherwise it will use JembeForm.load_init_param
            return config.form.load_init_param(value)
        return super().load_init_param(config, name, value)


class CForm(CFormBase):
    def __init__(self, form: Optional[JembeForm] = None):
        self.submited_record: Optional["Model"] = None
        super().__init__()

    @abstractmethod
    def get_record(self) -> Optional[Union["Model", dict]]:
        raise NotImplementedError()

    @run_only_once
    def mount(self):
        if self.state.form is None:
            record = self.get_record()
            if record is None:
                self.state.form = self._config.form()
            elif isinstance(record, dict):
                self.state.form = self._config.form(data=record)
            else:
                self.state.form = self._config.form(obj=record)

        self.state.form.mount(self)

    def display(self) -> "DisplayResponse":
        self.mount()
        if hasattr(self._config, "model") and hasattr(
            self._config.model, "__table_args__"
        ):
            self.model_info = self._config.model.__table_args__.get("info", dict())
        return super().display()

    def submit_form(
        self,
        submit_event: Optional[str] = None,
        submit_event_params: Optional[Callable[[Component], dict]] = None,
        submit_message: Optional[Union[Callable[[Component], str], str]] = None,
    ) -> bool:
        """Returns true if form is succesfully submited"""
        self.mount()
        if self.state.form.validate():
            try:
                record = self.get_record()
                if record is not None and not isinstance(record, dict):
                    self.submited_record = self.state.form.submit(self, record)
                else:
                    self.submited_record = self.state.form.submit(self)
                self.session.commit()
                if submit_event is not None:
                    se_params = (
                        dict()
                        if submit_event_params is None
                        else submit_event_params(self)
                    )
                    self.emit(submit_event, **se_params)
                if submit_message is not None:
                    se_message = (
                        submit_message
                        if isinstance(submit_message, str)
                        else submit_message(self)
                    )
                    self.emit("pushNotification", notification=Notification(se_message))
                return True
            except ValueError as error:
                self.emit(
                    "pushNotification", notification=Notification(str(error), "error")
                )
            except (sa.exc.SQLAlchemyError) as error:
                self.emit(
                    "pushNotification",
                    notification=Notification(
                        str(getattr(error, "orig", error))
                        if isinstance(error, sa.exc.SQLAlchemyError)
                        else str(error),
                        "error",
                    ),
                )
        self.session.rollback()
        return False
