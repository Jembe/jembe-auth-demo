from abc import ABCMeta
from typing import Any
from jembe import JembeInitParamSupport
from wtforms_sqlalchemy.orm import model_form as wtsa_model_form
from flask_sqlalchemy import SQLAlchemy
from wtforms.form import Form, FormMeta

__all__ = (
    "JembeForm",
    "model_form",
)


class JembeFormMeta(FormMeta, ABCMeta):
    pass


class JembeForm(JembeInitParamSupport, Form, metaclass=JembeFormMeta):
    @classmethod
    def dump_init_param(cls, value: Any) -> Any:
        return value.data if value is not None else dict()

    @classmethod
    def load_init_param(cls, value: Any) -> Any:
        return cls(data=value)


def model_form(
    model,
    db_session=None,
    base_class=JembeForm,
    only=None,
    exclude=None,
    field_args=None,
    converter=None,
    exclude_pk=True,
    exclude_fk=True,
    type_name=None,
):
    """
    Adds support for using db:SqlAlchemy instead of db.session() as db_session param
    """

    class DbSessionProxy:
        def __init__(self, db):
            self.db = db

        def query(self, *args, **kwargs):
            return self.db.session().query(*args, **kwargs)

    if db_session is not None and isinstance(db_session, SQLAlchemy):
        db_session = DbSessionProxy(db_session)

    return wtsa_model_form(
        model,
        db_session=db_session,
        base_class=base_class,
        only=only,
        exclude=exclude,
        field_args=field_args,
        converter=converter,
        exclude_pk=exclude_pk,
        exclude_fk=exclude_fk,
        type_name=type_name,
    )


model_form.__doc__ = wtsa_model_form.__doc__