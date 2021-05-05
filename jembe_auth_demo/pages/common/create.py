from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Iterable,
    Optional,
    Tuple,
    Type,
    Union,
)

from jembe_auth_demo.common import JembeForm
from .form import CForm
from jembe import Component, action

if TYPE_CHECKING:
    from jembe import ComponentRef, RedisplayFlag, ComponentConfig
    from flask_sqlalchemy import Model, SQLAlchemy

__all__ = ("CCreate",)


class CCreate(CForm):
    class Config(CForm.Config):
        default_template = "common/create.html"
        default_title = "Create"

        def __init__(
            self,
            db: "SQLAlchemy",
            form: "JembeForm",
            model: Type["Model"],
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

            super().__init__(
                db=db,
                form=form,
                template=template,
                components=components,
                inject_into_components=inject_into_components,
                redisplay=redisplay,
                changes_url=changes_url,
                url_query_params=url_query_params,
            )

    _config: Config

    def __init__(
        self, form: Optional[JembeForm] = None, is_modified: bool = False
    ) -> None:
        super().__init__(form=form)

    def get_record(self) -> Optional[Union["Model", dict]]:
        return self._config.model()

    @action
    def save(self) -> Optional[bool]:
        if self.submit_form(
            "save",
            lambda c: dict(record=c.submited_record, record_id=c.submited_record.id),
            lambda c: "{} saved".format(str(c.submited_record)),
        ):
            # don't redisplay
            return False
        return True

    @action
    def cancel(self, confirmed=False):
        if self.state.is_modified and not confirmed:
            self.request_confirmation(
                "cancel", "Cancel Add", "Are you sure, all changes will be lost?"
            )
        else:
            self.emit("cancel", record_id=None, record=None)
            return False
