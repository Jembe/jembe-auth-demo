from abc import ABCMeta
from typing import TYPE_CHECKING, Any, Optional
from jembe import JembeInitParamSupport
from wtforms.form import Form, FormMeta

if TYPE_CHECKING:
    from jembe import Component
    from jembe_auth_demo.pages.common.form import CForm
    from wtforms import Field
    from flask_sqlalchemy import Model
    from sqlalchemy.orm.session import Session


__all__ = ("JembeForm",)


class JembeFormMeta(FormMeta, ABCMeta):
    pass


class JembeForm(JembeInitParamSupport, Form, metaclass=JembeFormMeta):
    def __init__(
        self,
        formdata=None,
        obj=None,
        prefix="",
        data=None,
        meta=None,
        readonly=False,
        **kwargs
    ):
        self.is_readonly = readonly
        super().__init__(
            formdata=formdata, obj=obj, prefix=prefix, data=data, meta=meta, **kwargs
        )

    @classmethod
    def dump_init_param(cls, value: Any) -> Any:
        return value.data if value is not None else dict()

    @classmethod
    def load_init_param(cls, value: Any) -> Any:
        return cls(data=value)

    def mount(self, cform: "CForm") -> "JembeForm":
        return self

    def submit(
        self, cform: "CForm", record: Optional["Model"] = None
    ) -> Optional["Model"]:
        if record is not None:
            self.populate_obj(record)
            cform.session.add(record)
            return record
        return None

    def setdefault(self, field: "Field", param_name: str, value: Any) -> Any:
        if field.render_kw is None:
            field.render_kw = dict()
        return field.render_kw.setdefault(param_name, value)

    def set_readonly(self, *fields: "Field"):
        for field in fields:
            self.setdefault(field, "disabled", True)
            self.setdefault(field, "readonly", True)

    def set_readonly_all(self):
        self.set_readonly(*[field for field in self])