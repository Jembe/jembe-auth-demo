from abc import ABCMeta
from typing import TYPE_CHECKING, Any
from jembe import JembeInitParamSupport
from wtforms.form import Form, FormMeta

if TYPE_CHECKING:
    from jembe import Component


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

    def mount(self, component: "Component")-> "JembeForm":
        return self
