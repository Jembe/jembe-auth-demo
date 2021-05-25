from abc import ABCMeta
from typing import TYPE_CHECKING, Any, Optional
from jembe import JembeInitParamSupport, File
from wtforms.form import Form, FormMeta
from wtforms import FileField
from PIL import Image

if TYPE_CHECKING:
    from jembe_auth_demo.pages.common.form import CForm
    from wtforms import Field
    from flask_sqlalchemy import Model


__all__ = ("JembeForm", "JembeFileField", "JembeImageField")


class JembeFormMeta(FormMeta, ABCMeta):
    pass


class JembeForm(JembeInitParamSupport, Form, metaclass=JembeFormMeta):
    cform: "CForm"

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
        return (
            {
                k: v.dump_init_param(v) if isinstance(v, JembeInitParamSupport) else v
                for k, v in value.data.items()
            }
            if value is not None
            else dict()
        )

    @classmethod
    def load_init_param(cls, value: Any) -> Any:
        return cls(data=value)

    def mount(self, cform: "CForm") -> "JembeForm":
        self.cform = cform
        return self

    def submit(self, record: Optional["Model"] = None) -> Optional["Model"]:
        if record is not None:
            self.populate_obj(record)
            self.cform.session.add(record)
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


class JembeFileField(FileField):
    is_jembe_file_field = True

    def process_data(self, value):
        if value is None:
            self.data = None
        elif isinstance(value, File):
            self.data = value
        else:
            self.data = File.load_init_param(value)


class JembeImageField(JembeFileField):
    def __init__(
        self,
        label=None,
        validators=None,
        thumbnail_size=(400, 400),
        filters=tuple(),
        description="",
        id=None,
        default=None,
        widget=None,
        render_kw=None,
        _form=None,
        _name=None,
        _prefix="",
        _translations=None,
        _meta=None,
    ):
        super().__init__(
            label=label,
            validators=validators,
            filters=filters,
            description=description,
            id=id,
            default=default,
            widget=widget,
            render_kw=render_kw,
            _form=_form,
            _name=_name,
            _prefix=_prefix,
            _translations=_translations,
            _meta=_meta,
        )
        self._thumbnail_size = thumbnail_size

    def thumbnail(self) -> Optional["File"]:
        if self.data:
            thumb = self.data.get_cache_version(
                "thumbnail_{}_{}.jpg".format(*self._thumbnail_size)
            )
            if not thumb.exists():
                try:
                    with Image.open(self.data.open(mode="rb")) as img:
                        img.verify()
                except Exception:
                    return None
                with Image.open(self.data.open(mode="rb")) as img:
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    img.thumbnail(self._thumbnail_size)
                    with thumb.open("wb") as tfo:
                        img.save(tfo, "JPEG")
                        return thumb
            else:
                return thumb
        return None