from wtforms import Form, PasswordField, StringField, TextField, validators


class RegistrationForm(Form):
    name = StringField("Username", [validators.Length(min=4, max=25)])
    email = StringField("E-mail", [validators.Length(min=6, max=40)])
    password = PasswordField(
        "New Password",
        [
            validators.DataRequired(),
            validators.EqualTo("confirm", message="Passwords must match"),
        ],
    )
    confirm = PasswordField("Confirm Password")


class LoginForm(Form):
    name = StringField("Username", [validators.Length(min=4, max=40)])
    password = PasswordField()


class PostForm(Form):
    content = TextField("Post")


class MessageForm(Form):
    recipient = StringField("To")
    message = TextField("Message")
