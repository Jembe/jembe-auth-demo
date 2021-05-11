from typing import TYPE_CHECKING, Optional, Union
from flask_login.utils import logout_user
from jembe.component_config import listener
from wtforms import StringField, PasswordField, validators as val
from flask_login import login_user, current_user
from jembe import Component, action, config
from jembe_auth_demo.common import JembeForm
from jembe_auth_demo.pages.common import CForm, Notification, PComponent
from jembe_auth_demo.db import db
from jembe_auth_demo.models import User
from markupsafe import Markup

if TYPE_CHECKING:
    from jembe import DisplayResponse
    from flask_sqlalchemy import Model

__all__ = ("CLogin", "PCLogout", "CResetPassword", "CUserProfile")


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


class CUserProfile(Component):
    def init(self):
        if not current_user.is_authenticated:
            self.ac_deny()

    @listener(event="logout")
    def on_logout(self, event):
        self.ac_deny()

    @listener(event="login")
    def on_login(self, event):
        self.ac_allow()