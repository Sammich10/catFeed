# Include flask app and database
from app import get_db
# Import the flask app and associated libraries 
from flask import (
    Blueprint, Flask, render_template, Response, request, jsonify, redirect, url_for, session
)
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

from app.models import Owner

bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    """
    Decorator function to check if user is logged in

    Args: 
        f (function): The function to be decorated

    Returns: The decorated function if the user is logged in, otherwise 
    redirects the user to the login page
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        # If the 'logged-in' key is present in the session, allow the decorated function to proceed
        if 'logged-in' in session:
            return f(*args,**kwargs)
        else:
            # If the 'logged-in' key is not present in the session, redirect the user to the login page
            return redirect(url_for('auth.login'), Response=302)
    return wrap

@bp.route("/",methods=['GET'])
def root():
    """
    Handles the root route of the application. If the user is logged in,
    redirects them to the home page. Otherwise, redirects them to the login page

    Parameters:
        None

    Returns:
        None

    """
    if 'logged-in' in session:
        return redirect(url_for('catfeedapp.home'))
    else:
        return redirect(url_for('auth.login'), Response=302)

@bp.route("/login", methods=['GET','POST'])
def login():
    """
    Handles the login route of the application. If the request method is 'POST',
    it will check the username and password and log the user in. If the request
    method is 'GET', it will render the login page.

    Parameters:
        None

    Returns:
        The rendered login page or a redirect to the home page if the user is
        logged in.

    """
    error=None
    if request.method == 'POST':
        validate = validateLogin(request.form['username'], request.form['password'])
        if not validate[0]:
            error = validate[1]
        else:
            session['logged-in'] = True
            session['username'] = request.form['username']
            return redirect(url_for('catfeedapp.home'))
    return render_template('auth/login.html', error=error)

def validateLogin(username, password):
    """
    Checks if a user with the given username and password exists in the database.

    Parameters:
        username (str): The username of the user to check.
        password (str): The password of the user to check.

    Returns:
        True if the user exists in the database, False otherwise.
    """
    # Check if the user exists
    user = Owner.query.filter(Owner.username==username).first()
    if user is None:
        return (False, "User does not exist")
    # Check if the password is correct
    if not check_password_hash(user.password, password):
        return (False, "Password is incorrect")
    # User exists and password is correct
    return (True, "Success")

@bp.route("/register", methods=['GET','POST'])
def register():
    """    
    Handles the registration of a new user. If the request method is 'POST',
    it will add the new user to the database and log them in. If the request
    method is 'GET', it will render the registration page.
    
    Parameters:
        None
    
    Returns:
        The rendered registration page or a redirect to the home page if the
        user is logged in.
    
    errors: 
        None
    """
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        
        err = None
        # Validate the form
        if not username:
            err = 'Username is required'
        elif not email:
            err = 'Email is required'
        elif not password:
            err = 'Password is required'
        elif not verify_unique_email(email):
            err = 'Email already exists'
        # If no errors, attempt to add the user
        if err is not None:
            try: 
                add_owner(username, email, generate_password_hash(password))
            except db.IntegrityError:
                err = f"User {username} already exists"
            else:
                # User added successfully. Log them in
                session['logged-in'] = True
                session['username'] = username
                return redirect(url_for('catfeedapp.home'))
        # Some error occurred, return the error
        # resp = {'success': False, 'errors': err, 'info': None}
        # return jsonify(resp)
        return render_template('auth/register.html', error=err)
    return render_template('auth/register.html')

# Route for logging out
@bp.route("/logout")
@login_required
def logout():
    """
    Logs out the user and redirects them to the login page.
    
    Parameters:
        None
    
    Returns:
        A redirect to the login page
    """
    session.clear()
    return redirect(url_for('auth.login'))

def verify_unique_email(email):
    """
    Checks if an email address already exists in the database
    
    parameters:
        email (str): the email to check
    
    returns:
        True if the email already exists, False otherwise.
    """
    existingOwener = Owner.query.filter(Owner.email==email).first()
    if existingOwener is not None:
        print(f"Email {email} already exists")
        return True
    return False

@bp.before_app_request
def load_logged_in_user():
    """
    Loads the logged-in user from the session if they are logged in.
    
    Parameters:
        None
    
    Returns:
        None
    """
    user_id = session.get('username')
    if user_id is None:
        session.user = None
    else:
        session.user = Owner.query.filter(Owner.username==user_id).first()

def add_owner(username, email, password):
    """
    Adds a new owner entry to the database.

    Parameters:
        username (str): The new owner's username.
        email (str): The new owner's email.
        password (str): The new owner's password.

    Returns:
        None
    """
    db = get_db()
    new_owner = Owner(username = username, email = email, password = password)
    try:
        db.session.add(new_owner)
        db.session.commit()
    except db.IntegrityError:
        db.session.rollback()
        raise db.IntegrityError
    finally:
        db.session.close()

    return
