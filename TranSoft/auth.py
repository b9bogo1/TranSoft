import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from TranSoft.models import User
from TranSoft import db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        code = request.form['code']
        user = User.query.filter_by(email=email).first()
        error = None
        is_user_allowed = False

        file = open('TranSoft/allowed_users', 'r') # Open the file in read mode
        content = file.read() # Read the file content as a string
        file.close() # Close the file
        import json # Import the json module to parse the string as a list of dictionaries
        allowed_users = json.loads(content) # Parse the content as a list
        if allowed_users.count({'email': email, 'code': code}) > 0:
            is_user_allowed = True

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif not is_user_allowed:
            error = 'User not allowed to register or Wrong code provided'
        elif user:
            error = 'Email already exists.'

        if error is None:
            try:
                new_user = User(email=email, password=generate_password_hash(password),
                                firstname=firstname, lastname=lastname)
                db.session.add(new_user)
                db.session.commit()
            except db.IntegrityError:
                error = f"User {email} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        user = User.query.filter_by(email=email).first()
        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    from TranSoft.reading import XMTER_ID
    g.nodeId = XMTER_ID

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    return wrapped_view
