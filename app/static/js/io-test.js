// app/static/js/io-test.js

// Configuration for special ADC channel handling
const adcChannelConfig = {
    'mcp1-ch0': {
        type: 'percentage',
        targetElementId: 'mcp1-ch0'
    },
    'mcp1-ch1': {
        type: 'status',
        threshold: 2.5, // Voltage threshold for switching state
        targetElementId: 'mcp1-ch1-status',
        states: {
            active: { text: 'Ligado', className: 'status-active' },
            inactive: { text: 'Desligado', className: 'status-inactive' }
        }
    },
    'mcp1-ch2': {
        type: 'status',
        threshold: 2.5, // Voltage threshold
        targetElementId: 'mcp1-ch2-status',
        states: {
            active: { text: 'Aberto', className: 'status-active' },
            inactive: { text: 'Fechado', className: 'status-inactive' }
        }
    },
    'mcp1-ch3': {
        type: 'status',
        threshold: 2.5,
        targetElementId: 'mcp1-ch3-status',
        states: {
            active: { text: 'Aberto', className: 'status-active' },
            inactive: { text: 'Fechado', className: 'status-inactive' }
        }
    },
    'mcp1-ch4': {
        type: 'status',
        threshold: 2.5,
        targetElementId: 'mcp1-ch4-status',
        states: {
            active: { text: 'Ligado', className: 'status-active' },
            inactive: { text: 'Desligado', className: 'status-inactive' }
        }
    },
    'mcp1-ch5': {
        type: 'status',
        threshold: 2.5,
        targetElementId: 'mcp1-ch5-status',
        states: {
            active: { text: 'Ligado', className: 'status-active' },
            inactive: { text: 'Desligado', className: 'status-inactive' }
        }
    },
    'mcp1-ch6': {
        type: 'status',
        threshold: 2.5,
        targetElementId: 'mcp1-ch6-status',
        states: {
            active: { text: 'Aberto', className: 'status-active' },
            inactive: { text: 'Fechado', className: 'status-inactive' }
        }
    },
    'mcp1-ch7': {
        type: 'percentage',
        targetElementId: 'mcp1-ch7'
    },
        'mcp2-ch0': {
        type: 'status',
        threshold: 2.5,
        targetElementId: 'mcp2-ch0-status',
        states: {
            active: { text: 'Aberto', className: 'status-active' },
            inactive: { text: 'Fechado', className: 'status-inactive' }
        }
    }
};

// Update ADC values
function updateADCValues() {
    fetch('/api/adc-values')
        .then(response => response.json())
        .then(data => {
            // Update MCP1 values
            for (let i = 0; i < 8; i++) {
                const channelId = `mcp1-ch${i}`;
                const config = adcChannelConfig[channelId];
                const rawValue = data.mcp1[i];
                const voltage = (rawValue / 1023) * 3.3;

                if (config) {
                    // Handle special channels based on the configuration object
                    const element = document.getElementById(config.targetElementId);
                    if (!element) continue;

                    if (config.type === 'percentage') {
                        const percentage = (rawValue / 1023 * 100).toFixed(1);
                        element.textContent = percentage;
                    } else if (config.type === 'status') {
                        const baseClass = 'channel-status';
                        if (voltage >= config.threshold) {
                            element.textContent = config.states.active.text;
                            element.className = `${baseClass} ${config.states.active.className}`;
                        } else {
                            element.textContent = config.states.inactive.text;
                            element.className = `${baseClass} ${config.states.inactive.className}`;
                        }
                    }
                } else {
                    // Default behavior: display voltage
                    const element = document.getElementById(channelId);
                    if (element) {
                        element.textContent = voltage.toFixed(2);
                    }
                }
            }
            
           // Update MCP2 values
            for (let i = 0; i < 8; i++) {
                const channelId = `mcp2-ch${i}`;
                const config = adcChannelConfig[channelId];
                const rawValue = data.mcp2[i];
                const voltage = (rawValue / 1023) * 3.3;

                if (config) {
                    // Handle special channels based on the configuration object
                    const element = document.getElementById(config.targetElementId);
                    if (!element) continue;

                    if (config.type === 'status') {
                        const baseClass = 'channel-status';
                        if (voltage >= config.threshold) {
                            element.textContent = config.states.active.text;
                            element.className = `${baseClass} ${config.states.active.className}`;
                        } else {
                            element.textContent = config.states.inactive.text;
                            element.className = `${baseClass} ${config.states.inactive.className}`;
                        }
                    }
                } else {
                    // Default behavior: display voltage
                    const element = document.getElementById(channelId);
                    if (element) {
                        element.textContent = voltage.toFixed(2);
                    }
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

function setGpioState(gpio, state) {
    fetch('/api/set-gpio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ gpio, state }),
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            alert(`Failed to set GPIO ${gpio}: ${data.error}`);
        }
    })
    .catch(error => {
        console.error(`Error setting GPIO ${gpio}:`, error);
        alert(`Error setting GPIO ${gpio}: Network or server error`);
    });
}

// Set up GPIO push button event listeners
document.querySelectorAll('.gpio-push-button').forEach(button => {
    const gpio = button.dataset.gpio;

    const handlePress = () => {
        setGpioState(gpio, true);
        button.classList.add('active');
    };

    const handleRelease = () => {
        setGpioState(gpio, false);
        button.classList.remove('active');
    };

    // Mouse events
    button.addEventListener('mousedown', handlePress);
    button.addEventListener('mouseup', handleRelease);
    button.addEventListener('mouseleave', () => {
        if (button.classList.contains('active')) {
            handleRelease();
        }
    });

    // Touch events for mobile support
    button.addEventListener('touchstart', e => {
        e.preventDefault();
        handlePress();
    });
    button.addEventListener('touchend', handleRelease);
});

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