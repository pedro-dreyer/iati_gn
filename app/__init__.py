# app/__init__.py
import os
import sys
import atexit
from flask import Flask
from flask_session import Session

def create_app():
    app = Flask(__name__)
    
    print("=== Experiment Control System Startup ===")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Configure session
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_change_in_production')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
    
    print(f"Session directory: {app.config['SESSION_FILE_DIR']}")
    
    # Create session directory if it doesn't exist
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    
    # Initialize session
    try:
        Session(app)
        print("Session initialization successful")
    except Exception as e:
        print(f"ERROR initializing session: {e}")
    
    # Initialize database
    print("Initializing database...")
    from . import db
    app.teardown_appcontext(db.close_db)
    
    try:
        with app.app_context():
            db.init_db()
    except Exception as e:
        print(f"ERROR during database initialization: {e}")
    
    # Initialize Raspberry Pi I/O
    print("Initializing Raspberry Pi I/O...")
    from . import pi_io
    try:
        pi_io.init_hardware()
        pi_io.start_simulation()  # Start sensor simulation if in simulation mode
        print("Raspberry Pi I/O initialized")
        
        # Register cleanup function to run on application exit
        atexit.register(pi_io.cleanup)
    except Exception as e:
        print(f"ERROR initializing Raspberry Pi I/O: {e}")
    
    # Register blueprints
    from .routes import main as main_blueprint
    from .auth import auth as auth_blueprint
    from .api import api as api_blueprint
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(api_blueprint)
    
    print("Application initialized successfully")
    print("===================================")
    
    return app