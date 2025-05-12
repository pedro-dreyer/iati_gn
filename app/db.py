# app/db.py
import os
import hashlib
import duckdb
from flask import g

DB_PATH = 'experiment_system.duckdb'

def get_db():
    """Connect to DuckDB database and return connection."""
    if 'db' not in g:
        g.db = duckdb.connect(DB_PATH)
        # We'll use standard DuckDB functionality without extensions
    return g.db

def close_db(e=None):
    """Close the database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database with tables."""
    try:
        conn = duckdb.connect(DB_PATH)
        
        # Create sequences for each table
        conn.execute("CREATE SEQUENCE IF NOT EXISTS user_id_seq")
        conn.execute("CREATE SEQUENCE IF NOT EXISTS reading_id_seq")
        conn.execute("CREATE SEQUENCE IF NOT EXISTS experiment_id_seq")
        
        # Create users table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username VARCHAR UNIQUE NOT NULL,
            password VARCHAR NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create sensor_readings table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY,
            sensor_tag VARCHAR NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            value REAL NOT NULL,
            experiment_id INTEGER
        )
        ''')
        
        # Create experiments table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            fuel_type VARCHAR NOT NULL,
            hydrogen_usage VARCHAR,
            hydrogen_type VARCHAR,
            test_duration INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.close()
        print("Database initialized successfully.")
        
        # Test the database connection
        if not test_db_connection():
            print("WARNING: Database connection test failed!")
        
        # Ensure a test user exists
        ensure_test_user()
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        # Continue execution even if there's an error
        # The application might still work with partial functionality

def hash_password(password):
    """Hash a password for storing."""
    salt = os.urandom(32)  # A new salt for this user
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000  # Number of iterations
    )
    # Store salt:key
    return salt.hex() + ':' + key.hex()

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user."""
    salt_str, key_str = stored_password.split(':')
    salt = bytes.fromhex(salt_str)
    stored_key = bytes.fromhex(key_str)
    new_key = hashlib.pbkdf2_hmac(
        'sha256',
        provided_password.encode('utf-8'),
        salt,
        100000  # Same number of iterations as used for hashing
    )
    return new_key == stored_key

def create_user(username, password):
    """Create a new user with the given username and password."""
    db = get_db()
    hashed_password = hash_password(password)
    
    try:
        # Check if username already exists
        result = db.execute(
            "SELECT COUNT(*) FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        
        if result[0] > 0:
            print(f"Username {username} already exists")
            return False
            
        # Get next ID from sequence
        next_id = db.execute("SELECT nextval('user_id_seq')").fetchone()[0]
            
        # Insert the new user with explicit ID
        db.execute(
            "INSERT INTO users (id, username, password) VALUES (?, ?, ?)",
            (next_id, username, hashed_password)
        )
        print(f"User {username} created successfully with ID {next_id}")
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def authenticate_user(username, password):
    """Authenticate a user by username and password."""
    db = get_db()
    result = db.execute(
        "SELECT id, username, password FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    
    if result and verify_password(result[2], password):
        return {"id": result[0], "username": result[1]}
    return None

# Add this to app/db.py

def test_db_connection():
    """Test if the database connection works correctly."""
    try:
        db = duckdb.connect(DB_PATH)
        result = db.execute("SELECT 1").fetchone()
        db.close()
        if result[0] == 1:
            print("Database connection test successful!")
            return True
        else:
            print("Database connection test failed: Unexpected result")
            return False
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False

def ensure_test_user():
    """Ensure that a test user exists."""
    try:
        db = duckdb.connect(DB_PATH)
        
        # Check if 'admin' user exists
        result = db.execute(
            "SELECT COUNT(*) FROM users WHERE username = 'admin'"
        ).fetchone()
        
        if result[0] == 0:
            # Make sure sequence exists
            db.execute("CREATE SEQUENCE IF NOT EXISTS user_id_seq")
            
            # Create tables if they don't exist
            db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username VARCHAR UNIQUE NOT NULL,
                password VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Get next ID from sequence
            next_id = db.execute("SELECT nextval('user_id_seq')").fetchone()[0]
            
            # Create admin user with password 'admin'
            hashed_password = hash_password('admin')
            db.execute(
                "INSERT INTO users (id, username, password) VALUES (?, 'admin', ?)",
                (next_id, hashed_password)
            )
            print(f"Created test user 'admin' with password 'admin' (ID: {next_id})")
        else:
            print("Test user 'admin' already exists")
        
        db.close()
        return True
    except Exception as e:
        print(f"Error ensuring test user: {e}")
        return False