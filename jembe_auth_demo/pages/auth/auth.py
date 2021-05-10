from typing import TYPE_CHECKING, Optional, Union
from flask_login.utils import logout_user
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

__all__ = ("CLogin", "CLogout", "CResetPassword", "CUserProfile")


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

    def submit(
        self, cform: "CForm", record: Optional["Model"] = None
    ) -> Optional["Model"]:
        user = cform.session.query(User).filter_by(email=self.email.data).first()
        if user and user.check_password(password=self.password.data):
            login_user(user)
            return user
        else:
            raise ValueError("Invalid user/password combination")


@config(CForm.Config(db=db, form=LoginForm))
class CLogin(CForm):
    def init(self):
        if current_user.is_authenticated:
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
        return True

    def display(self) -> "DisplayResponse":
        self.emit("setPageTitle", title="Login")
        return super().display()


@config(PComponent.Config(changes_url=False))
class CLogout(PComponent):
    def __init__(self, active:bool=False):
        super().__init__()

    def init(self):
        if not current_user.is_authenticated:
            self.ac_deny()

    @action
    def logout(self):
        logout_user()
        self.ac_deny()
        self.emit("logout")
        self.state.active = False

    @action
    def cancel(self):
        self.state.active = False


class CResetPassword(Component):
    def init(self):
        if not current_user.is_authenticated:
            self.ac_deny()


class CUserProfile(Component):
    def init(self):
        if not current_user.is_authenticated:
            self.ac_deny()
