from typing import TYPE_CHECKING, Optional, Union
from flask_login.utils import logout_user
from jembe.component_config import listener
from wtforms import StringField, PasswordField, FileField, validators as val
from wtforms.fields.html5 import EmailField
from flask_login import login_user, current_user
from jembe import Component, action, config
from jembe_auth_demo.common import JembeForm, JembeImageField
from jembe_auth_demo.pages.common import CForm, Notification, PComponent, CFormBase
from jembe_auth_demo.db import db
from jembe_auth_demo.models import User
from markupsafe import Markup

if TYPE_CHECKING:
    from jembe import DisplayResponse
    from flask_sqlalchemy import Model

__all__ = ("CLogin", "PCLogout", "CResetPassword", "CUserProfile", "CEditUserProfile")


class LoginForm(JembeForm):
    email = StringField(
        "Email",
        validators=[
            val.DataRequired("Email is required."),
            val.Email(message="Enter a valid email."),
        ],
    )
    password = PasswordField(
        "Password", validators=[val.DataRequired("Password is required.")]
    )

    def submit(self, record: Optional["Model"] = None) -> Optional["Model"]:
        user = self.cform.session.query(User).filter_by(email=self.email.data).first()
        if user and user.check_password(password=self.password.data):
            login_user(user)
            return user
        else:
            raise ValueError("Invalid user/password combination")


class PasswordResetForm(JembeForm):
    old_password = PasswordField(
        "Old Password", validators=[val.DataRequired("Old Password is required")]
    )
    new_password = PasswordField(
        validators=[
            val.DataRequired(),
            val.Length(
                min=7, max=User.password.type.length, message="Select stronger password"
            ),
        ]
    )
    confirm_password = PasswordField(
        validators=[val.EqualTo("new_password", message="Passwords must match")]
    )

    def validate_old_password(form, field):
        if not current_user.is_authenticated:
            raise ValueError("In order to change password you must be logged in!")
        if not current_user.check_password(password=field.data):
            raise ValueError("Invalid password")

    def submit(self, record: Optional["Model"] = None) -> Optional["Model"]:
        if current_user.is_authenticated:
            user: User = current_user._get_current_object()
            user.set_password(self.new_password.data)
            self.old_password.data = None
            self.new_password.data = None
            self.confirm_password.data = None
            return user
        return None


class UserProfileForm(JembeForm):
    first_name = StringField(
        validators=[
            val.DataRequired(),
            val.Length(max=User.first_name.type.length),
        ]
    )
    last_name = StringField(
        validators=[
            val.DataRequired(),
            val.Length(max=User.last_name.type.length),
        ]
    )

    email = EmailField(
        validators=[
            val.DataRequired(),
            val.Email(),
            val.Length(max=User.email.type.length),
        ]
    )
    photo = JembeImageField()

    def mount(self, cform: "CForm") -> "JembeForm":
        if isinstance(cform, CUserProfile):
            self.set_readonly_all()

        if self.photo.data and self.photo.data.is_just_uploaded():
            if self.photo.validate(self):
                self.photo.data.move_to_temp()
            else:
                self.photo.data = None
        return super().mount(cform)

    def submit(self, record: Optional["Model"] = None) -> Optional["Model"]:
        if self.photo.data and self.photo.data.in_temp_storage():
            self.photo.data.move_to_public()
        if record and record.photo and record.photo != self.photo.data:
            record.photo.remove()
            record.photo = None
        return super().submit(record=record)


@config(CForm.Config(db=db, form=LoginForm))
class CLogin(CForm):
    def init(self):
        if current_user.is_authenticated:
            self.ac_deny()

    @listener(event="logout")
    def on_logout(self, event):
        self.ac_deny()

    def get_record(self) -> Optional[Union["Model", dict]]:
        return None

    @action
    def login(self):
        if self.submit_form(
            "login",
            submit_message=lambda c: "User {} {} logged in".format(
                current_user.first_name, current_user.last_name
            ),
        ):
            return False

        if self.state.form and self.state.form.errors:
            self.emit(
                "pushNotification",
                notification=Notification(
                    Markup(
                        "<br>".join(
                            v for a in self.state.form.errors.values() for v in a
                        )
                    ),
                    "error",
                ),
            )
        self.ac_deny()
        return True

    def display(self) -> "DisplayResponse":
        self.emit("setPageTitle", title="Login")
        return super().display()


@config(PComponent.Config(changes_url=False))
class PCLogout(PComponent):
    def __init__(self, active: bool = False):
        super().__init__()

    def init(self):
        if not current_user.is_authenticated:
            self.ac_deny()

    @listener(event="login")
    def on_login(self, event):
        self.ac_allow()

    @action
    def logout(self):
        logout_user()
        self.emit("logout")
        self.state.active = False
        self.ac_deny()
        return True

    @action
    def cancel(self):
        self.state.active = False


@config(CForm.Config(db=db, form=PasswordResetForm))
class CResetPassword(CForm):
    def init(self):
        if not current_user.is_authenticated:
            self.ac_deny()

    @listener(event="logout")
    def on_logout(self, event):
        self.ac_deny()

    @listener(event="login")
    def on_login(self, event):
        self.ac_allow()

    def get_record(self) -> Optional[Union["Model", dict]]:
        return (
            current_user._get_current_object()
            if current_user.is_authenticated
            else None
        )

    @action
    def reset_password(self):
        return self.submit_form("reset_password", submit_message="Password changed")


@config(
    CForm.Config(
        db=db,
        form=UserProfileForm,
        title=lambda self: "User Profile: {} {}".format(
            self.get_record().first_name, self.get_record().last_name
        ),
    )
)
class CUserProfile(CForm):
    def init(self):
        if not current_user.is_authenticated:
            self.ac_deny()

    @listener(event="logout")
    def on_logout(self, event):
        self.ac_deny()

    @listener(event="login")
    def on_login(self, event):
        self.ac_allow()

    def get_record(self) -> Optional[Union["Model", dict]]:
        return current_user._get_current_object()


@config(
    CForm.Config(
        db=db,
        form=UserProfileForm,
        title=lambda self: "Update Profile: {} {}".format(
            self.get_record().first_name, self.get_record().last_name
        ),
    )
)
class CEditUserProfile(CForm):
    def __init__(self, form: Optional[JembeForm] = None, is_modified: bool = False):
        super().__init__(form=form)

    def init(self):
        if not current_user.is_authenticated:
            self.ac_deny()

    @listener(event="logout")
    def on_logout(self, event):
        self.ac_deny()

    @listener(event="login")
    def on_login(self, event):
        self.ac_allow()

    def get_record(self) -> Optional[Union["Model", dict]]:
        return current_user._get_current_object()

    @action
    def save(self) -> Optional[bool]:
        if self.submit_form(
            "save",
            lambda c: dict(record=c.submited_record, record_id=c.submited_record.id),
            lambda c: "{} saved".format(str(c.submited_record)),
        ):
            # don't redisplay component
            return False
        return True

    @action
    def cancel(self, confirmed=False):
        if self.state.is_modified and not confirmed:
            self.request_confirmation(
                "cancel", "Cancel Update", "Are you sure, all changes will be lost?"
            )
        else:
            self.emit(
                "cancel", record_id=self.get_record().id, record=self.get_record()
            )
            return False
