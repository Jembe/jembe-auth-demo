from jembe_auth_demo.pages.common.read import CReadWithDelete
from typing import Optional, TYPE_CHECKING
from jembe_auth_demo.common.forms import JembeForm, JembeImageField
from jembe import config, listener
from jembe_auth_demo.db import db
from jembe_auth_demo.pages.common import (
    CCrudTable,
    TableColumn as TC,
    CCreate,
    ActionLink,
    CUpdate,
    CDelete,
)
from jembe_auth_demo.models import User, Group
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SelectMultipleField,
    validators,
)
from wtforms.fields.html5 import EmailField
import sqlalchemy as sa
from flask_login import current_user

if TYPE_CHECKING:
    from jembe import Component
    from flask_sqlalchemy import Model

__all__ = ("CUsers",)


class UserForm(JembeForm):
    first_name = StringField(
        validators=[
            validators.DataRequired(),
            validators.Length(max=User.first_name.type.length),
        ]
    )
    last_name = StringField(
        validators=[
            validators.DataRequired(),
            validators.Length(max=User.last_name.type.length),
        ]
    )

    email = EmailField(
        validators=[
            validators.DataRequired(),
            validators.Email(),
            validators.Length(max=User.email.type.length),
        ]
    )
    active = BooleanField(default=True)
    groups_ids = SelectMultipleField(coerce=int)

    photo = JembeImageField()

    def mount(self, component: "Component"):
        if self.is_readonly:
            self.set_readonly_all()
            self.groups_ids.choices = [
                (g.id, g.title)
                for g in db.session.query(Group).filter(
                    Group.id.in_(self.groups_ids.data)
                )[:100]
            ]
        else:
            self.groups_ids.choices = [
                (g.id, g.title) for g in db.session.query(Group)[:100]
            ]

        if self.photo.data and self.photo.data.is_just_uploaded():
            # if new file is uploaded validate it and move to temp storage
            # or set it to None
            if self.photo.validate(self):
                self.photo.data.move_to_temp()
            else:
                self.photo.data = None
        return super().mount(component)

    def submit(self, record: Optional["Model"] = None) -> Optional["Model"]:
        if self.photo.data and self.photo.data.in_temp_storage():
            # move photo in public storage for permanent keep
            self.photo.data.move_to_public()
        if record and record.photo and record.photo != self.photo.data:
            # delete old photo when it's replaced with new one
            record.photo.remove()
            record.photo = None
        return super().submit(record=record)


class CreateUserForm(UserForm):
    password = PasswordField(
        validators=[
            validators.DataRequired(),
            validators.Length(
                min=7, max=User.password.type.length, message="Select stronger password"
            ),
        ]
    )
    confirm_password = PasswordField(
        validators=[validators.EqualTo("password", message="Passwords must match")]
    )

    def submit(self, record: Optional["Model"] = None) -> Optional["Model"]:
        user: Optional[User] = super().submit(record)
        if user is not None:
            user.set_password(self.password.data)
        return user


class UpdateUserForm(UserForm):
    new_password = PasswordField()
    confirm_password = PasswordField(
        validators=[validators.EqualTo("new_password", message="Passwords must match")]
    )

    def submit(self, record: Optional["Model"] = None) -> Optional["Model"]:
        user: Optional[User] = super().submit(record)
        if user is not None and self.new_password.data:
            user.set_password(self.new_password.data)
        return user


@config(
    CCrudTable.Config(
        db=db,
        title="Users",
        query=sa.orm.Query(User).order_by(User.first_name),
        columns=[
            TC(User.first_name),
            TC(User.last_name),
            TC(User.email),
        ],
        components=dict(
            create=(
                CCreate,
                CCreate.Config(
                    db=db, model=User, form=CreateUserForm, title="Add User"
                ),
            ),
            read=(
                CReadWithDelete,
                CReadWithDelete.Config(
                    db=db,
                    model=User,
                    form=UserForm,
                    top_menu=[
                        ActionLink(
                            lambda self: self.component(  # type:ignore
                                "../update",
                                id=self.record.id,  # type:ignore
                                _record=self.record,  # type:ignore
                            ),
                            "Edit",
                        ),
                        ActionLink(
                            lambda self: self.component().call(  # type:ignore
                                "delete_record"
                            ),
                            "Delete",
                        ),
                    ],
                ),
            ),
            update=(CUpdate, CUpdate.Config(db=db, model=User, form=UpdateUserForm)),
            delete=(CDelete, CDelete.Config(db=db, model=User)),
        ),
        top_menu=[ActionLink("create", "Add")],
        record_menu=[
            ActionLink(
                lambda self, record: self.component(  # type:ignore
                    "read", id=record.id, _record=record
                ),
                "View",
            ),
            ActionLink(
                lambda self, record: self.component(  # type:ignore
                    "update", id=record.id, _record=record
                ),
                "Edit",
            ),
            ActionLink(
                lambda self, record: self.component(  # type:ignore
                    "delete", id=record.id, _record=record
                ),
                "Delete",
            ),
        ],
    )
)
class CUsers(CCrudTable):
    def init(self):
        if not current_user.is_authenticated:
            self.ac_deny()

    @listener(event="delete", source="read")
    def on_delete(self, event):
        self.state.display_mode = None