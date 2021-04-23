from typing import TYPE_CHECKING, Optional, Union
from wtforms import StringField, PasswordField, validators as val
from flask_login import login_user
from jembe import Component, action
from jembe_auth_demo.common import JembeForm
from jembe_auth_demo.pages.common import Notification
from jembe_auth_demo.db import db
from jembe_auth_demo.models import User
import sqlalchemy as sa
from markupsafe import Markup

if TYPE_CHECKING:
    from flask import Response

__all__ = ("CLogin", "CResetPassword")


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


class CLogin(Component):
    def __init__(self, form: Optional[LoginForm] = None):
        super().__init__()

    def mount(self):
        if self.state.form is None:
            self.state.form = LoginForm()
        self.state.form.mount(self)

    @action
    def login(self):
        self.mount()
        if self.state.form.validate():
            try:
                db.session.query(User).get
                user = User.query.filter_by(email=self.state.form.email.data).first()
                if user and user.check_password(password=self.state.form.password.data):
                    login_user(user)
                    self.emit(
                        "pushNotification",
                        notification=Notification(
                            "User {} {} logged in".format(
                                user.first_name, user.last_name
                            )
                        ),
                    )
                    self.emit("login")
                    return False
                else:
                    self.state.form = None
                    self.emit(
                        "pushNotification",
                        notification=Notification(
                            "Invalid user/password combination", "error"
                        ),
                    )
            except (sa.exc.SQLAlchemyError) as error:
                self.emit(
                    "pushNotification",
                    notification=Notification(
                        str(getattr(error, "orig", error))
                        if isinstance(error, sa.exc.SQLAlchemyError)
                        else str(error),
                        "error",
                    ),
                )
        if self.state.form and self.state.form.errors:
            self.emit(
                "pushNotification",
                notification=Notification(
                    Markup(
                        "<br>".join(v for a in self.state.form.errors.values() for v in a)
                    ),
                    "error",
                ),
            )
        return True

    def display(self) -> Union[str, "Response"]:
        self.mount()
        self.emit("setPageTitle", title="Login")
        return super().display()


class CResetPassword(Component):
    pass