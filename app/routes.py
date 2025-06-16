# app/routes.py
from flask import Blueprint, render_template, g, request, redirect, url_for
from .auth import login_required
from . import db
import os

main = Blueprint('main', __name__)

@main.context_processor
def inject_header_config():
    """Injects a list of header logos into all templates based on an environment variable."""
    client = os.environ.get('APP_CLIENT', 'breitener').lower()
    
    logos = [
        'images/breitener.png',
        'images/iati.png',
        'images/suape_energia.png'
    ] # Default for 'breitener'
    
    if client == 'kps':
        logos = [
            'images/kps.png',
            'images/iati.png'
        ]
    
    return dict(header_logos=logos)

@main.route('/')
@login_required
def index():
    return render_template('input_output_test.html')

@main.route('/experiment-data')
@login_required
def experiment_data():
    return render_template('experiment_data.html')

@main.route('/configuration')
@login_required
def configuration():
    return render_template('configuration.html')

# Route to handle experiment setup form submission
@main.route('/save-experiment', methods=['POST'])
@login_required
def save_experiment():
    if request.method == 'POST':
        # Get form data
        fuel_type = request.form.get('fuel')
        hydrogen_usage = request.form.get('assistance')
        test_duration = request.form.get('test_time')
        hydrogen_type = request.form.get('hydrogen_source')
        
        # Validate data
        if not fuel_type or not test_duration:
            # Handle validation error
            return redirect(url_for('main.index'))
        
        # Save experiment to database
        conn = db.get_db()
        conn.execute(
            """
            INSERT INTO experiments 
            (user_id, fuel_type, hydrogen_usage, hydrogen_type, test_duration) 
            VALUES (?, ?, ?, ?, ?)
            """,
            (g.user['id'], fuel_type, hydrogen_usage, hydrogen_type, test_duration)
        )
        
        return redirect(url_for('main.experiment_data'))
    
    return redirect(url_for('main.index'))