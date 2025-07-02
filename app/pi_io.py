# app/pi_io.py
import time
import threading
import json
import platform
import os
from datetime import datetime

# Check if running on Raspberry Pi
def is_raspberry_pi():
    try:
        with open('/proc/device-tree/model', 'r') as m:
            if 'raspberry pi' in m.read().lower():
                return True
    except:
        pass
    return False

# Set hardware mode based on platform
HARDWARE_AVAILABLE = is_raspberry_pi()

# Only import RPi.GPIO and spidev if running on Raspberry Pi
if HARDWARE_AVAILABLE:
    try:
        import RPi.GPIO as GPIO
        import spidev
        HARDWARE_AVAILABLE = True
        print("Raspberry Pi hardware detected. Running in hardware mode.")
    except ImportError:
        print("WARNING: RPi.GPIO or spidev not available. Running in simulation mode.")
        HARDWARE_AVAILABLE = False
else:
    print("Non-Raspberry Pi system detected. Running in simulation mode.")
    # Create mock modules for GPIO and spidev
    class MockGPIO:
        BCM = 11
        OUT = 0
        IN = 1
        HIGH = 1
        LOW = 0
        
        @staticmethod
        def setmode(mode):
            pass
            
        @staticmethod
        def setup(pin, mode):
            pass
            
        @staticmethod
        def output(pin, value):
            pass
            
        @staticmethod
        def input(pin):
            return 0
            
        @staticmethod
        def cleanup():
            pass
            
        class PWM:
            def __init__(self, pin, freq):
                self.pin = pin
                self.freq = freq
                self.dc = 0
                
            def start(self, dc):
                self.dc = dc
                
            def ChangeDutyCycle(self, dc):
                self.dc = dc
                
            def stop(self):
                pass
    
    # Mock SpiDev class
    class MockSpiDev:
        def __init__(self):
            self.max_speed_hz = 0
            
        def open(self, bus, device):
            pass
            
        def xfer2(self, data):
            # Return mock data - 3 bytes as in MCP3008 protocol
            return [0, 0, 0]
            
        def close(self):
            pass
    
    # Set mock classes
    GPIO = MockGPIO()
    spidev = type('spidev', (), {'SpiDev': MockSpiDev})
    spidev.SpiDev = MockSpiDev

# GPIO assignments
GPIO_PINS = {
    2: "ABRIR/FECHAR DIESEL",
    3: "ABRIR/FECHAR OB1",
    23: "ABRIR/FECHAR OCA1",
    17: "CHAVE GERAL DO MOTOGERADOR",
    27: "LIGA/DESLIGA MOTOR",
    22: "LIGA/DESLIGA ELETROLISADOR",
    0: "BOMBA H2",
    13: "LIGAR/DESLIGAR INJETOR",
    12: "DESLIZANTE PRÉ BOMBA (PWM)",
}

# PWM pins
PWM_PINS = [12]

# Simulation data
adc_values = {
    'mcp1': [0] * 8,
    'mcp2': [0] * 8
}

gpio_states = {}
pwm_instances = {}

# Lock for thread safety
io_lock = threading.Lock()

def init_hardware():
    """Initialize GPIO and SPI if hardware is available."""
    with io_lock:
        for pin in GPIO_PINS:
            gpio_states[pin] = False  # Logical "OFF"

        for pin in PWM_PINS:
            # For PWM, 0% is the initial logical "OFF" state
            gpio_states[f"pwm_{pin}"] = 0

    if not HARDWARE_AVAILABLE:
        print("Hardware initialization skipped (simulation mode)")
        return

    GPIO.setmode(GPIO.BCM)
    for pin in GPIO_PINS:
        if pin in PWM_PINS:
            GPIO.setup(pin, GPIO.OUT)
            pwm_instances[pin] = GPIO.PWM(pin, 10)
            pwm_instances[pin].start(0)  # Physical 0% duty cycle
        else:
            GPIO.setup(pin, GPIO.OUT)
            # For inverted logic, HIGH on pin is "OFF"
            GPIO.output(pin, GPIO.HIGH) 
            # gpio_states[pin] is already False, which matches physical HIGH (OFF)


    # Initialize SPI for MCP3008
    try:
        # We have two MCP3008 chips on separate SPI channels
        global spi_mcp1, spi_mcp2
        spi_mcp1 = spidev.SpiDev()
        spi_mcp1.open(0, 0)  # Bus 0, Device 0
        spi_mcp1.max_speed_hz = 1000000  # 1MHz

        spi_mcp2 = spidev.SpiDev()
        spi_mcp2.open(0, 1)  # Bus 0, Device 1
        spi_mcp2.max_speed_hz = 1000000  # 1MHz
    except Exception as e:
        print(f"Error initializing SPI: {e}")

def cleanup():
    """Clean up GPIO resources."""
    if HARDWARE_AVAILABLE:
        for pin in PWM_PINS:
            if pin in pwm_instances:
                pwm_instances[pin].stop()
        GPIO.cleanup()

def read_adc(chip, channel):
    """Read the specified ADC channel on the specified MCP3008 chip."""
    if not HARDWARE_AVAILABLE:
        # Return simulated ADC value
        if chip == 1:
            return adc_values['mcp1'][channel]
        else:
            return adc_values['mcp2'][channel]

    try:
        spi = spi_mcp1 if chip == 1 else spi_mcp2
        # MCP3008 protocol: Start bit (1), single-ended (1), channel (3 bits), 000 padding
        r = spi.xfer2([1, (8 + channel) << 4, 0])
        # Combine the two bytes to get the 10-bit ADC value
        value = ((r[1] & 3) << 8) + r[2]
        return value
    except Exception as e:
        print(f"Error reading ADC: {e}")
        return 0

def read_all_adc():
    """Read all ADC channels from both MCP3008 chips."""
    with io_lock:
        # Read from MCP1 (all 8 channels)
        for i in range(8):
            adc_values['mcp1'][i] = read_adc(1, i)

        # Read from MCP2 (all 8 channels)
        for i in range(8):
            adc_values['mcp2'][i] = read_adc(2, i)

        return adc_values

def get_gpio_states():
    """Get the current state of all GPIO pins (reflecting UI logic)."""
    states = {}

    with io_lock:
        if HARDWARE_AVAILABLE:
            for pin_key in GPIO_PINS: # Iterate using the keys from GPIO_PINS
                pin_number = int(pin_key)

                if pin_number in PWM_PINS:
                    # PWM state is stored directly as UI-intended duty cycle
                    states[str(pin_number)] = gpio_states.get(f"pwm_{pin_number}", 0)
                else:
                    try:
                        # Physical HIGH means logical "OFF" (False)
                        # Physical LOW means logical "ON" (True)
                        physical_state_is_high = GPIO.input(pin_number) == GPIO.HIGH
                        states[str(pin_number)] = not physical_state_is_high
                    except Exception as e:
                        # Fallback to stored state on error
                        print(f"Error reading GPIO {pin_number}: {e}. Using stored state.")
                        states[str(pin_number)] = gpio_states.get(pin_number, False)
        else:
            # Simulation mode: return directly from gpio_states
            for pin_key in GPIO_PINS:
                pin_number = int(pin_key)
                if pin_number in PWM_PINS:
                    states[str(pin_number)] = gpio_states.get(f"pwm_{pin_number}", 0)
                else:
                    states[str(pin_number)] = gpio_states.get(pin_number, False)

    response = {}
    for pin, state in states.items():
        pin_number = int(pin) if isinstance(pin, str) else pin
        if pin_number in PWM_PINS:
            if 'pwm' not in response:
                response['pwm'] = {}
            response['pwm'][str(pin_number)] = state
        else:
            response[str(pin_number)] = state

    return response


def set_gpio(pin, state):
    """Set a GPIO pin. UI 'state' (True=ON, False=OFF) is inverted for physical output."""
    pin = int(pin)

    if pin not in GPIO_PINS:
        return {"success": False, "error": f"Invalid GPIO pin: {pin}"}

    if pin in PWM_PINS:
        return {"success": False, "error": f"GPIO {pin} is a PWM pin. Use set_pwm instead."}

    with io_lock:
        # Store the UI-intended state
        gpio_states[pin] = state 

        if HARDWARE_AVAILABLE:
            try:
                # Invert logic for physical output:
                # UI "ON" (state=True) -> physical LOW
                # UI "OFF" (state=False) -> physical HIGH
                physical_output = GPIO.LOW if state else GPIO.HIGH
                GPIO.output(pin, physical_output)
                return {"success": True}
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            # Simulation mode: just update the logical state
            return {"success": True}

def set_pwm(pin, duty_cycle):
    """Set the PWM duty cycle for a GPIO pin."""
    pin = int(pin)
    duty_cycle = int(duty_cycle)
    
    if pin not in PWM_PINS:
        return {"success": False, "error": f"GPIO {pin} is not a PWM pin"}
    
    if duty_cycle < 0 or duty_cycle > 100:
        return {"success": False, "error": f"Duty cycle must be between 0 and 100, got {duty_cycle}"}
    
    with io_lock:
        gpio_states[f"pwm_{pin}"] = duty_cycle
        
        if HARDWARE_AVAILABLE:
            try:
                pwm_instances[pin].ChangeDutyCycle(duty_cycle)
                return {"success": True}
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            # Simulation mode
            return {"success": True}

def simulate_sensor_values():
    """Simulate changing sensor values for testing."""
    import random

    TEST_VALUE = 3
    TEST_VALUE = TEST_VALUE * 1023 / 3.3
    
    with io_lock:
        # Generate realistic looking values
        for i in range(8):
            # Randomize around a base value to simulate real sensor readings
            base_value = i * 100  # Different base value for each channel
            variation = random.randint(-50, 50)  # Random variation
            
            # Keep values within 0-1023 range (10-bit ADC)
            adc_values['mcp1'][i] = max(0, min(1023, base_value + variation))
            adc_values['mcp2'][i] = max(0, min(1023, base_value + variation + 50))
        
        adc_values['mcp1'][0] = TEST_VALUE
        adc_values['mcp1'][1] = TEST_VALUE
        adc_values['mcp1'][2] = TEST_VALUE
        adc_values['mcp1'][3] = TEST_VALUE
        adc_values['mcp1'][4] = TEST_VALUE
        adc_values['mcp1'][5] = TEST_VALUE
        adc_values['mcp1'][6] = TEST_VALUE
        adc_values['mcp1'][7] = TEST_VALUE

# Start a background thread to simulate sensor values when in simulation mode
def start_simulation():
    """Start a background thread to simulate sensor values."""
    if not HARDWARE_AVAILABLE:
        print("Starting sensor simulation thread...")
        def simulation_thread():
            while True:
                simulate_sensor_values()
                time.sleep(1)
        
        thread = threading.Thread(target=simulation_thread, daemon=True)
        thread.start()
    else:
        print("Simulation not started (hardware mode active)")

# Data logging functionality
def log_sensor_data(experiment_id=None):
    """Log sensor data to database."""
    from . import db
    
    data = read_all_adc()
    timestamp = datetime.now()
    
    try:
        conn = db.get_db()
        
        # Make sure the sequence exists
        conn.execute("CREATE SEQUENCE IF NOT EXISTS reading_id_seq")
        
        for chip in [1, 2]:
            for channel in range(8):
                # Create a tag for the sensor
                if chip == 1:
                    if channel == 0:
                        tag = "MOTOR_ATIVO"
                    elif channel == 1:
                        tag = "SENSOR_H2_AMBIENTES"
                    elif channel == 2:
                        tag = "ABERTO_FECHADO_GN"
                    elif channel == 3:
                        tag = "ABERTO_FECHADO_H2"
                    elif channel == 4:
                        tag = "PRE_INJECAO_GN"
                    elif channel == 5:
                        tag = "PRESSAO_ELETROLISADOR"
                    elif channel == 6:
                        tag = "VALVULA_ARMAZENADO"
                    elif channel == 7:
                        tag = "VALVULA_ELETROLISADO"
                else:
                    if channel == 0:
                        tag = "BOMBA_ELETROLISADO"
                    else:
                        tag = f"MCP2_CH{channel}"
                
                value = data[f'mcp{chip}'][channel]
                
                # Get next ID from sequence
                next_id = conn.execute("SELECT nextval('reading_id_seq')").fetchone()[0]
                
                # Log to database with explicit ID
                conn.execute(
                    """
                    INSERT INTO sensor_readings 
                    (id, sensor_tag, timestamp, value, experiment_id) 
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (next_id, tag, timestamp, value, experiment_id)
                )
        
        return True
    except Exception as e:
        print(f"Error logging sensor data: {e}")
        return False