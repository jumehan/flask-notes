"""Flask app for Cupcakes"""

from flask import Flask, request, render_template, redirect, session, flash
from models import db, connect_db, User, Note
from forms import RegisterForm, LoginForm, CSRFProtectForm, NewNoteForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_notes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "oh-so-secret"
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)



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
        if User.query.filter_by(username=username).one_or_none() or User.query.filter_by(email=email).one_or_none() is not None:
            form.username.errors = ["Username/Email already taken"]
            return render_template("register.html", form=form)

        user = User.register(username, password, email, first_name, last_name)
        db.session.add(user)
        db.session.commit()

        session["username"] = user.username

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
            session["username"] = user.username  # keep logged in
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
    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/")

    #Authorization
    if session["username"] != username:
        flash("You're not allowed here!")

        return redirect (f"/users/{session['username']}")


    else:
        return render_template("user.html", user=user, form=form)

@app.post("/logout")
def logout():
    """Log user out and redirects to homepage"""

    form = CSRFProtectForm()

    if form.validate_on_submit:
        # Remove "username" if present, but no errors if it wasn't
        flash("Logout successful")
        session.pop("username", None)

    return redirect("/")

# GET /users/<username>
# Show information about the given user.

# Show all of the notes a user has given.

# For each note, display with a link to a form to edit the note and a button to delete the note.

# Have a link that sends you to a form to add more notes and a button to delete the entire user account, including their notes.

# POST /users/<username>/delete
# Remove the user from the database and make sure to also delete all of their notes. Clear any user information in the session and redirect to /.

# As with the logout route, make sure you have CSRF protection for this.

# GET /users/<username>/notes/add
# Display a form to add notes.
@app.route("/users/<username>/notes/add", methods=["GET", "POST"])
def notes_add(username):
    """Add a new note."""

    owner = User.query.get_or_404(username)

    form = NewNoteForm()

    if form.validate_on_submit:
        title = form.title.data
        content = form.content.data

        note = Note(title=title, content=content, owner=owner)

        db.session.add(note)
        db.session.commit()

        return redirect(f'/users/{username}')

    return render_template("note.html", form=form)
    
# POST /users/<username>/notes/add
# Add a new note and redirect to /users/<username>
# GET /notes/<note-id>/update
# Display a form to edit a note.
# POST /notes/<note-id>/update
# Update a note and redirect to /users/<username>.
# POST /notes/<note-id>/delete
# Delete a note and redirect to /users/<username>.

# As with the logout and delete routes, make sure you have CSRF protection for this.
