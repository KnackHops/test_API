import functools

from flask import Blueprint, g, flash, render_template, request, url_for, redirect, session

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# creates the blueprint
# (name of the bp, points to where the bp is. in this case the auth.py, the prefix for the view functions. Must be included when using url_for )
bp = Blueprint("auth",__name__,url_prefix="/auth")

# loads before any view is called
# checks if session exists, therefore user is logged in
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/register', methods=('GET','POST'))
def register():
    # if GET, ie just going to the site
    # the template will be served
    # which in turn, when the template form is submitted
    # POST will be the method and so, the block of actual
    # registration is executed
    # note: if there is an error, template wil rerender
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        if not username:
            error = "Username is required!"
        elif not password:
            error = "Password is required!"
        # checks if fetchone is empty
        # db.execute sends a query to the database
        # if username already exists, fetchone will have a value
        # fetchone gets the first row from the query
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f'User {username} is already registered.'
        
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            
            db.commit()
            return redirect(url_for('auth.login'))
        
        flash(error)
    
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET','POST'))
def login():
    # GET, and POST works the same way as register
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)   
        ).fetchone()
        
        if user is None:
            error = "Incorrect username!"
        if not check_password_hash(user['password'], password):
            error = "Incorrect password!"
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)
        
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# decorator for required login
# takes a function view, which is the view arguement
# wraps that view with another function
# if g.user is None, meaning user is not logged in
# session is empty
# the user will be redirected to login
# if not, the user will continue to the wrapped view
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    return wrapped_view