"""Flask app for Cupcakes"""

from flask import Flask, request, render_template, redirect, session, flash
from models import db, connect_db, User
from forms import RegisterForm, LoginForm, CSRFProtectForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_notes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "oh-so-secret"
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
# db.create_all() - do this in ipython


@app.get("/")
def root():
    """Redirect to /register"""
    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user: produce form & handle form submission."""

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        # check if user/email is already registered to an account
        # try db.session commit and if there's an error do try-except SQLA Integrity Error
        if User.query.filter_by(username=username).count() > 0:
            #one_or_None or one and make sure it's not None
            #do username =.. or email=..
            form.username.errors = ["Username already taken"]
            return render_template("register.html", form=form)

        if User.query.filter_by(email=email).count() > 0:
            form.email.errors = ["Email already taken"]
            return render_template("register.html", form=form)

        user = User.register(username, password, email, first_name, last_name)
        db.session.add(user)
        db.session.commit()

        session["user_username"] = user.username #put session["username"] and set it as global constant

        # on successful login, redirect to secret page
        return redirect(f"/users/{username}")

    else:
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(username, password)

        if user:
            session["user_username"] = user.username  # keep logged in
            return redirect(f"/users/{username}")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)
# end-login


@app.get("/users/<username>")
def show_user_profile(username):
    """Example hidden page for logged-in users only."""
    form = CSRFProtectForm()
    user = User.query.get_or_404(username)

    #Authentication
    if "user_username" not in session:
        flash("You must be logged in to view!")
        return redirect("/")

    #Authorization
    if session["user_username"] != username:
        flash("You're not allowed here!")

        return redirect (f"/users/{session['user_username']}")


    else:
        return render_template("user.html", user=user, form=form)

@app.post("/logout")
def logout():
    """Log user out and redirects to homepage"""

    form = CSRFProtectForm()

    if form.validate_on_submit:
        # Remove "user_username" if present, but no errors if it wasn't
        flash("Logout successful")
        session.pop("user_username", None)

    return redirect("/")


