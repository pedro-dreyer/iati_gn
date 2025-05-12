# run.py
from app import create_app
import os

# Create directory for Flask session files if it doesn't exist
os.makedirs('flask_session', exist_ok=True)

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)