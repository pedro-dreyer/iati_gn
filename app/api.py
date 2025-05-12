# app/api.py
from flask import Blueprint, jsonify, request, g
from . import pi_io
from .auth import login_required

api = Blueprint('api', __name__)

@api.route('/api/adc-values')
@login_required
def get_adc_values():
    """API endpoint to get the current ADC values."""
    values = pi_io.read_all_adc()
    return jsonify(values)

@api.route('/api/gpio-states')
@login_required
def get_gpio_states():
    """API endpoint to get the current GPIO states."""
    states = pi_io.get_gpio_states()
    return jsonify(states)

@api.route('/api/set-gpio', methods=['POST'])
@login_required
def set_gpio():
    """API endpoint to set a GPIO pin."""
    data = request.json
    
    if not data or 'gpio' not in data or 'state' not in data:
        return jsonify({"success": False, "error": "Missing required parameters: gpio, state"})
    
    try:
        gpio = int(data['gpio'])
        state = bool(data['state'])
        
        result = pi_io.set_gpio(gpio, state)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@api.route('/api/set-pwm', methods=['POST'])
@login_required
def set_pwm():
    """API endpoint to set a PWM duty cycle."""
    data = request.json
    
    if not data or 'gpio' not in data or 'value' not in data:
        return jsonify({"success": False, "error": "Missing required parameters: gpio, value"})
    
    try:
        gpio = int(data['gpio'])
        value = int(data['value'])
        
        result = pi_io.set_pwm(gpio, value)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@api.route('/api/log-sensor-data', methods=['POST'])
@login_required
def log_sensor_data():
    """API endpoint to manually trigger sensor data logging."""
    experiment_id = request.json.get('experiment_id') if request.json else None
    
    try:
        success = pi_io.log_sensor_data(experiment_id)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Failed to log sensor data"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})