# app/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from functools import wraps
from . import db

auth = Blueprint('auth', __name__)

def login_required(f):
    """Decorator to require login for views."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@auth.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db.authenticate_user(username, password)
        
        if user:
            # Successfully authenticated
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            # Redirect to the next page or to home
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            return redirect(next_page)
        else:
            error = 'Nome de usuário ou senha inválidos.'
    
    return render_template('login.html', error=error)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Debug output
        print(f"Signup attempt for username: {username}")
        
        # Validate input
        if not username or not password:
            error = 'Nome de usuário e senha são obrigatórios.'
            print("Error: Username and password are required")
        elif password != confirm_password:
            error = 'As senhas não conferem.'
            print("Error: Passwords do not match")
        else:
            # Try to create the user
            if db.create_user(username, password):
                print(f"User {username} created successfully, redirecting to login")
                flash('Conta criada com sucesso! Por favor, faça login.')
                return redirect(url_for('auth.login'))
            else:
                error = 'Não foi possível criar a conta. Nome de usuário já existe.'
                print(f"Failed to create user {username}, likely already exists")
    
    return render_template('signup.html', error=error)

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth.before_app_request
def load_logged_in_user():
    """Load user info if logged in."""
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        # You could fetch more user details here if needed
        g.user = {
            'id': session.get('user_id'),
            'username': session.get('username')
        }