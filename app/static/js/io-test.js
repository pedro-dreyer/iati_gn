// app/static/js/io-test.js

// Apply the header images
const upper_header_string = `<img src="static/images/breitener.png" class="img-fluid" alt="Image 1">
<img src="static/images/iati.png" class="img-fluid" alt="Image 2">
<img src="static/images/suape_energia.png" class="img-fluid" alt="Image 3">`;

const upper_header = document.getElementById('upper_header');
upper_header.innerHTML = upper_header_string;

// Update ADC values
function updateADCValues() {
    fetch('/api/adc-values')
        .then(response => response.json())
        .then(data => {
            // Update MCP1 values
            for (let i = 0; i < 8; i++) {
                const element = document.getElementById(`mcp1-ch${i}`);
                if (element) {
                    // Convert raw ADC value to voltage (0-1023 to 0-3.3V)
                    const voltage = (data.mcp1[i] / 1023 * 3.3).toFixed(2);
                    element.textContent = voltage;
                }
            }
            
            // Update MCP2 values
            for (let i = 0; i < 8; i++) {
                const element = document.getElementById(`mcp2-ch${i}`);
                if (element) {
                    // Convert raw ADC value to voltage (0-1023 to 0-3.3V)
                    const voltage = (data.mcp2[i] / 1023 * 3.3).toFixed(2);
                    element.textContent = voltage;
                }
            }
        })
        .catch(error => {
            console.error('Error fetching ADC values:', error);
        });
}

// Update GPIO values
function updateGPIOStates() {
    fetch('/api/gpio-states')
        .then(response => response.json())
        .then(data => {
            // Update GPIO checkboxes without triggering change events
            Object.keys(data).forEach(gpio => {
                const element = document.getElementById(`gpio${gpio}`);
                if (element) {
                    element.checked = data[gpio];
                }
            });
            
            // Update PWM sliders
            if (data.pwm) {
                Object.keys(data.pwm).forEach(gpio => {
                    const element = document.getElementById(`pwm-gpio${gpio}`);
                    const valueElement = document.getElementById(`pwm-gpio${gpio}-value`);
                    if (element && valueElement) {
                        element.value = data.pwm[gpio];
                        valueElement.textContent = `${data.pwm[gpio]}%`;
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error fetching GPIO states:', error);
        });
}

// Set up GPIO toggle event listeners
document.querySelectorAll('.gpio-toggle').forEach(toggle => {
    toggle.addEventListener('change', function() {
        const gpio = this.id.replace('gpio', '');
        const state = this.checked;
        
        fetch('/api/set-gpio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                gpio: gpio,
                state: state
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                // Revert toggle if operation failed
                this.checked = !state;
                alert(`Failed to set GPIO ${gpio}: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error setting GPIO:', error);
            // Revert toggle if operation failed
            this.checked = !state;
            alert(`Error setting GPIO ${gpio}: Network or server error`);
        });
    });
});

// Set up PWM slider event listeners
document.querySelectorAll('.pwm-slider').forEach(slider => {
    const valueElement = document.getElementById(`${slider.id}-value`);
    
    // Update display value when slider changes
    slider.addEventListener('input', function() {
        valueElement.textContent = `${this.value}%`;
    });
    
    // Send value to server when slider is released
    slider.addEventListener('change', function() {
        const gpio = this.id.replace('pwm-gpio', '');
        const value = parseInt(this.value);
        
        fetch('/api/set-pwm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                gpio: gpio,
                value: value
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                alert(`Failed to set PWM for GPIO ${gpio}: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error setting PWM:', error);
            alert(`Error setting PWM for GPIO ${gpio}: Network or server error`);
        });
    });
});

// Set up log data button
const logDataButton = document.getElementById('log-data-button');
const logStatus = document.getElementById('log-status');

if (logDataButton) {
    logDataButton.addEventListener('click', function() {
        logStatus.textContent = 'Registrando valores...';
        logStatus.className = 'log-status log-status-pending';
        
        fetch('/api/log-sensor-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                logStatus.textContent = 'Valores registrados com sucesso!';
                logStatus.className = 'log-status log-status-success';
                
                // Clear success message after 3 seconds
                setTimeout(() => {
                    logStatus.textContent = '';
                    logStatus.className = 'log-status';
                }, 3000);
            } else {
                logStatus.textContent = `Erro: ${data.error}`;
                logStatus.className = 'log-status log-status-error';
            }
        })
        .catch(error => {
            console.error('Error logging data:', error);
            logStatus.textContent = 'Erro de rede ao registrar dados';
            logStatus.className = 'log-status log-status-error';
        });
    });
}

// Initial update
updateADCValues();
updateGPIOStates();

// Set up periodic updates
setInterval(updateADCValues, 1000); // Update ADC values every second
setInterval(updateGPIOStates, 5000); // Update GPIO states every 5 seconds