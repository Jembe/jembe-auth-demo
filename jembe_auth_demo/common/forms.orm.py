from abc import ABCMeta
import inspect
from typing import Callable, Dict, Optional, TYPE_CHECKING, Any, Union
from jembe import JembeInitParamSupport
import wtforms
from wtforms.form import Form, FormMeta

if TYPE_CHECKING:
    from wtforms import Field
    import sqlalchemy as sa
    from flask_sqlalchemy import Model, SQLAlchemy

__all__ = (
    "JembeForm",
    "sa_field",
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


class SaFieldConvertor:
    def __init__(self) -> None:
        self.converters: Dict[str, Callable] = {
            "String": self.conv_String,
            "Text": self.conv_Text,
            "LargeBinary": self.conv_Text,
            "Binary": self.conv_Text,
            "Boolean": self.conv_Boolean,
            "dialects.mssql.base.BIT": self.conv_Boolean,
            "Date": self.conv_Date,
            "DateTime": self.conv_DateTime,
            "Enum": self.conv_Enum,
            "Integer": self.handle_integer_types,
            "Numeric": self.handle_decimal_types,
            "dialects.mysql.types.YEAR": self.conv_MSYear,
            "dialects.mysql.base.YEAR": self.conv_MSYear,
            "dialects.postgresql.base.INET": self.conv_PGInet,
            "dialects.postgresql.base.MACADDR": self.conv_PGMacaddr,
            "dialects.postgresql.base.UUID": self.conv_PGUuid,
            "MANYTOONE": self.conv_ManyToOne,
            "MANYTOMANY": self.conv_ManyToMany,
            "ONETOMANY": self.conv_ManyToMany,
        }

    def convert(
        self,
        model: "Model",
        prop: "sa.orm.properties.ColumnProperty",
        db: Optional["SQLAlchemy"],
    ) -> "Field":
        if not hasattr(prop, "columns") and not hasattr(prop, "direction"):
            return
        elif not hasattr(prop, "direction") and len(prop.columns) != 1:
            raise TypeError(
                "Do not know how to convert multiple-column properties currently"
            )

        kwargs: dict = dict(
            validators=[], filters=[], default=None, description=prop.doc
        )
        if kwargs["validators"]:
            # Copy to prevent modifying nested mutable values of the original
            kwargs["validators"] = list(kwargs["validators"])

        converter = None
        column = None
        if not hasattr(prop, "direction"):
            column = prop.columns[0]
            # Support sqlalchemy.schema.ColumnDefault, so users can benefit
            # from  setting defaults for fields, e.g.:
            #   field = Column(DateTimeField, default=datetime.utcnow)

            default = getattr(column, "default", None)

            if default is not None:
                # Only actually change default if it has an attribute named
                # 'arg' that's callable.
                callable_default = getattr(default, "arg", None)

                if callable_default is not None:
                    # ColumnDefault(val).arg can be also a plain value
                    default = (
                        callable_default(None)
                        if callable(callable_default)
                        else callable_default
                    )

            kwargs["default"] = default

            converter = self._get_converter(column)
        else:
            # We have a property with a direction.
            if db is None:
                raise ValueError("Cannot convert field %s, need DB session." % prop.key)

            foreign_model = prop.mapper.class_

            nullable = True
            for pair in prop.local_remote_pairs:
                if not pair[0].nullable:
                    nullable = False

            kwargs.update(
                {
                    "allow_blank": nullable,
                    "query_factory": lambda: db.session.query(foreign_model).all(),
                }
            )

            converter = self.converters[prop.direction.name]

        return converter(column=column, field_args=kwargs)

    def _get_converter(self, column: "sa.Column") -> Callable:
        types = inspect.getmro(type(column.type))
        # Search by module + name
        for ctype in types:
            type_name = "{}.{}".format(ctype.__module__, ctype.__name__)
            if type_name.startswith("sqlalchemy."):
                type_name = type_name[11:]
            if type_name in self.converters:
                return self.converters[type_name]
        # Search by name
        for ctype in types:
            if ctype.__name__ in self.converters:
                return self.converters[ctype.__name__]

        raise ValueError(
            "Do not know how to convert column '{}.{}' ({}) to form field.".format(
                column.class_.__name__, column.name, types[0]
            )
        )


    def _apply_require_validators(self, column, field_args):
        if column.nullable:
            field_args["validators"].append(wtforms.validators.Optional())
        else:
            field_args["validators"].append(wtforms.validators.DataRequired())
        return field_args
    def conv_String(self, column: "sa.Column", field_args, **extra) -> "Field":
        field_args = self._apply_require_validators(column, field_args)
        if isinstance(column.type.length, int) and column.type.length:
            field_args["validators"].append(
                wtforms.validators.Length(max=column.type.length)
            )
        return wtforms.StringField(**field_args)

    def conv_Text(self, column: "sa.Column", field_args, **extra) -> "Field":
        field_args = self._apply_require_validators(column, field_args)
        if isinstance(column.type.length, int) and column.type.length:
            field_args["validators"].append(
                wtforms.validators.Length(max=column.type.length)
            )
        return wtforms.TextAreaField(**field_args)

    def conv_Boolean(self, column: "sa.Column", field_args, **extra) -> "Field":
        return wtforms.BooleanField(**field_args)

    def conv_Date(self, column: "sa.Column", field_args, **extra) -> "Field":
        field_args = self._apply_require_validators(column, field_args)
        return wtforms.DateField(**field_args)

    def conv_DateTime(self, column: "sa.Column", field_args, **extra) -> "Field":
        field_args = self._apply_require_validators(column, field_args)
        return wtforms.DateTimeField(**field_args)

    def conv_Enum(self, column: "sa.Column", field_args, **extra) -> "Field":
        field_args = self._apply_require_validators(column, field_args)
        field_args["choices"] = [(e, e) for e in column.type.enums]
        return wtforms.SelectField(**field_args)

    def handle_integer_types(
        self, column: "sa.Column", field_args, **extra
    ) -> "Field":
        field_args = self._apply_require_validators(column, field_args)
        unsigned = getattr(column.type, "unsigned", False)
        if unsigned:
            field_args["validators"].append(wtforms.validators.NumberRange(min=0))
        return wtforms.IntegerField(**field_args)

    def handle_decimal_types(
        self, column: "sa.Column", field_args, **extra
    ) -> "Field":
        field_args = self._apply_require_validators(column, field_args)
        # override default decimal places limit, use database defaults instead
        field_args.setdefault("places", None)
        return wtforms.DecimalField(**field_args)

    def conv_MSYear(self, column: "sa.Column", field_args, **extra) -> "Field":
        field_args = self._apply_require_validators(column, field_args)
        field_args["validators"].append(
            wtforms.validators.NumberRange(min=1901, max=2155)
        )
        return wtforms.StringField(**field_args)

    def conv_PGInet(self, column: "sa.Column", field_args, **extra) -> "Field":
        field_args = self._apply_require_validators(column, field_args)
        field_args.setdefault("label", "IP Address")
        field_args["validators"].append(wtforms.validators.IPAddress())
        return wtforms.StringField(**field_args)

    def conv_PGMacaddr(self, column: "sa.Column", field_args, **extra) -> "Field":
        field_args = self._apply_require_validators(column, field_args)
        field_args.setdefault("label", "MAC Address")
        field_args["validators"].append(wtforms.validators.MacAddress())
        return wtforms.StringField(**field_args)

    def conv_PGUuid(self, column: "sa.Column", field_args, **extra) -> "Field":
        field_args = self._apply_require_validators(column, field_args)
        field_args.setdefault("label", "UUID")
        field_args["validators"].append(wtforms.validators.UUID())
        return wtforms.StringField(**field_args)

    def conv_ManyToOne(self, column: "sa.Column", field_args, **extra) -> "Field":
        field_args = self._apply_require_validators(column, field_args)
        # return QuerySelectField(**field_args)
        raise NotImplementedError()

    def conv_ManyToMany(self, column: "sa.Column", field_args, **extra) -> "Field":
        field_args = self._apply_require_validators(column, field_args)
        # return QuerySelectMultipleField(**field_args)
        raise NotImplementedError()


sa_field_convertor = SaFieldConvertor()


def sa_field(
    column: Union["sa.Column", str],
    model: Optional["Model"] = None,
    db: Optional["SQLAlchemy"] = None,
) -> "Field":
    """
    Creates wtform field based on SqlAlchemy column definition,
    chosing field type and adding appropriate validations
    """
    global sa_field_convertor
    if isinstance(column, str) and model is None:
        raise ValueError("model is required if column '{}' is string".format(column))
    if model is None:
        model = column.class_  # type:ignore

    column_name = column if isinstance(column, str) else column.name

    mapper = model._sa_class_manager.mapper
    for prop in mapper.iterate_properties:
        if prop.key == column_name:
            return sa_field_convertor.convert(model=model, prop=prop, db=db)
    raise ValueError(
        "Invalid column {} of model {}{}.".format(
            column_name, model.__module__, model.__name__
        )
    )
