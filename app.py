import datetime

from flask import Flask, redirect, render_template, request, session, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, MessageForm, PostForm, RegistrationForm
from sqlalchemy import ForeignKey, or_
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:postgres@localhost/your_db_name"
app.config["SECRET_KEY"] = "very secret key"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String)
    password = db.Column(db.String)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)

    author_id = db.Column(db.Integer, ForeignKey("user.id"))

    author = db.relationship("User", foreign_keys=author_id)
    date = db.Column(db.DateTime)

    def __init__(self, content, author, date):
        self.content = content
        self.author = author
        self.date = date


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String)

    sender_id = db.Column(db.Integer, ForeignKey("user.id"))
    recipient_id = db.Column(db.Integer, ForeignKey("user.id"))

    sender = db.relationship("User", foreign_keys=sender_id)
    recipient = db.relationship("User", foreign_keys=recipient_id)

    def __init__(self, message, sender, recipient):
        self.message = message
        self.sender = sender
        self.recipient = recipient


@app.route("/")
def index():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)


@app.route("/<username>")
def user_page(username):
    if session.get("logged_in") is True:
        user = User.query.filter(User.name == username).first()
        posts = Post.query.filter(Post.author == user).all()
        return render_template("index.html", posts=posts)
    return render_template(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    message = None
    if request.method == "POST":
        try:
            user = User(
                name=form.name.data, email=form.email.data, password=form.password.data
            )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("index"))
        except IntegrityError:
            message = "User already exist "
    return render_template("register.html", form=form, message=message)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    message = None
    if request.method == "POST":
        user = User.query.filter(User.name == form.name.data).first()
        if user and check_password_hash(user.password, form.password.data) is True:
            session["username"] = user.name
            session["logged_in"] = True
        else:
            message = "Wrong data!"
    return render_template("login.html", form=form, message=message)


@app.route("/logout")
def logout():
    session.clear()
    session["logged_in"] = False
    return redirect(url_for("login"))


@app.route("/add_post", methods=["GET", "POST"])
def add_post():
    if session.get("logged_in") is True:
        form = PostForm(request.form)
        if request.method == "POST":
            user = User.query.filter(User.name == session["username"]).first()
            post = Post(
                content=form.content.data, author=user, date=datetime.datetime.now()
            )
            db.session.add(post)
            db.session.commit()
            return redirect(url_for("index"))
        return render_template("new_post.html", form=form)
    else:
        return redirect(url_for("login"))


@app.route("/send_message", methods=["GET", "POST"])
def send_message():
    form = MessageForm(request.form)
    if session.get("logged_in") is True:
        if request.method == "POST":
            recipient = User.query.filter(User.name == form.recipient.data).first()
            sender = User.query.filter(User.name == session["username"]).first()
            message = Message(
                message=form.message.data, sender=sender, recipient=recipient
            )
            db.session.add(message)
            db.session.commit()
            return redirect(url_for("messages"))
        else:
            return render_template("send_message.html", form=form)
    return redirect(url_for("login"))


@app.route("/messages/<username>")
def messages(username):
    sender = User.query.filter(User.name == username).first()
    recipient = User.query.filter(User.name == username).first()
    msg = Message.query.filter(
        or_(Message.sender == sender, Message.recipient == recipient)
    ).all()
    return render_template("message_box.html", messages=msg)


@app.route("/inbox/<username>")
def inbox(username):
    if session.get("logged_in") is True:
        recipient = User.query.filter(User.name == username).first()
        msg = Message.query.filter(Message.recipient == recipient).all()
        return render_template("messages.html", messages=msg)
    return redirect(url_for("login"))


@app.route("/outbox/<username>")
def outbox(username):
    sender = User.query.filter(User.name == username).first()
    msg = Message.query.filter(Message.sender == sender).all()
    return render_template("messages.html", messages=msg)


if __name__ == "__main__":
    app.run()
