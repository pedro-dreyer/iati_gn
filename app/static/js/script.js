const upper_header_string = `<img src="static/images/breitener.png" class="img-fluid" alt="Image 1">
<img src="static/images/iati.png" class="img-fluid" alt="Image 2">
<img src="static/images/suape_energia.png" class="img-fluid" alt="Image 3">`

const upper_header = document.getElementById('upper_header');
upper_header.innerHTML = upper_header_string;

// const radioLabels = document.querySelectorAll('.btn-group-toggle label');

// Add event listeners
// radioLabels.forEach((label) => {
//     label.addEventListener('click', (event) => {
//         // Save state of all radio buttons
//         radioLabels.forEach((label) => {
//             const radioButton = label.querySelector('input[type=radio]');
//             localStorage.setItem(radioButton.id, radioButton.checked);
//             console.log(radioButton.id, radioButton.checked);
//         });
//     });
// });

// Load state from localStorage on page load
// window.onload = function() {
//     radioLabels.forEach((label) => {
//         const radioButton = label.querySelector('input[type=radio]');
//         const storedState = localStorage.getItem(radioButton.id);

//         radioButton.checked = storedState === 'true';

//         // Add an event listener to save the state of the radio button when it is changed
//         radioButton.addEventListener('change', () => {
//             localStorage.setItem(radioButton.id, radioButton.checked);
//         });
//     });
// };

// $(document).ready(function() {
//     // Remove the 'active' class from the currently active button
//     // $('.btn-group-toggle .btn.active').removeClass('focus');
//     // $('.btn-group-toggle .btn.active').removeClass('active');

//     // Add the 'active' class to the button with id 'OCA1'
//     // $('#OCA1').parent().addClass('focus');
//     $('#OCA1').parent().addClass('active');
// });

var radioButtons = document.querySelectorAll('input[type=radio]');
var textInputs = document.querySelectorAll('input[type=text]');

// Add event listener to each radio button
radioButtons.forEach(function(radioButton) {
    radioButton.addEventListener('change', function() {
        // select other radio buttons in the same group
        var otherRadioButtons = document.querySelectorAll('input[type=radio][name="' + radioButton.name + '"]');
        // set value of other radio buttons to false
        otherRadioButtons.forEach(function(otherRadioButton) {
            if (otherRadioButton !== radioButton) {
                sessionStorage.setItem(otherRadioButton.id, false);
            }
        });
        sessionStorage.setItem(radioButton.id, radioButton.checked);
    });
});

// Load state from localStorage
radioButtons.forEach(function(radioButton) {
    var checked = sessionStorage.getItem(radioButton.id);
    if (checked === 'true') {
        radioButton.checked = true;
    } else if (checked === 'false') {
        radioButton.checked = false;
    }
});

// button states
let general_button = false
let start_motor_button = false
let stop_motor_button = false
let start_test_button = false

let engine_temp_timer = false 

// // Add event listener to each text input
// textInputs.forEach(function(textInput) {
//     textInput.addEventListener('input', function() {
//         // Save value to localStorage
//         sessionStorage.setItem(textInput.id, textInput.value);
//     });
// });

// // Load value from localStorage
// textInputs.forEach(function(textInput) {
//     var value = sessionStorage.getItem(textInput.id);
//     if (value !== null) {
//         textInput.value = value;
//     }
// });

// Add event listener to each button to change its color when clicked
// document.querySelectorAll('.button').forEach(function(button) {
//     button.addEventListener('click', function() {
//         this.classList.toggle('button-clicked');
//     });
// });


// start_test button 
document.getElementById('start_test_button').addEventListener('click', function() {
    if (document.getElementById('engine_temp').classList.contains('info-color') && engine_temp_timer){ 
        this.classList.toggle('button-clicked');

        if (document.getElementById('ocb1').checked) { 
            document.getElementById('retorno_ocb1').classList.toggle('info-color'); 
            document.getElementById('injecao_ocb1').classList.toggle('info-color');
    
        } else if (document.getElementById('oca1').checked){
            document.getElementById('retorno_oca1').classList.toggle('info-color');
            document.getElementById('injecao_oca1').classList.toggle('info-color');
        }

        setTimeout(function() {
            document.getElementById('injecao_diesel').classList.toggle('info-color');
            document.getElementById('retorno_diesel').classList.toggle('info-color');

            if (document.getElementById('hydrogen_eletrolisado').checked) { 
                document.getElementById('h2_eletrolisado').classList.toggle('info-color');
            } else if (document.getElementById('hydrogen_armazenado').checked){
                document.getElementById('h2_armazenado').classList.toggle('info-color');
                
            }

        }, 5000); // 

       
    }
});



// General button
document.getElementById('general_button').addEventListener('click', function() {

    this.classList.toggle('button-clicked');
    if (document.getElementById('ocb1').checked) { 
        document.getElementById('aquecimento_ocb1').classList.toggle('info-color'); 
        setTimeout(function() {
            document.getElementById('densidade_ocb1').classList.toggle('info-color');
        }, 5000); // 
    } else if (document.getElementById('oca1').checked){
        document.getElementById('aquecimento_oca1').classList.toggle('info-color');
        setTimeout(function() {
            document.getElementById('densidade_oca1').classList.toggle('info-color');
        }, 5000); //
    }
});


// start_motor button 
document.getElementById('start_motor').addEventListener('click', function() {
    if (document.getElementById('densidade_ocb1').classList.contains('info-color') || document.getElementById('densidade_oca1').classList.contains('info-color')) { 
        this.classList.toggle('button-clicked');
        
        setTimeout(function() {
            document.getElementById('injecao_diesel').classList.toggle('info-color');
            document.getElementById('retorno_diesel').classList.toggle('info-color');
            document.getElementById('motor_ativo').classList.toggle('info-color');
        }, 1000);

        setTimeout(function() {
            document.getElementById('engine_temp').classList.toggle('info-color');
            setTimeout(function() {
                engine_temp_timer = true;
            }, 5000); // 
        }, 5000);
    } 
});





// let isChecked = false;

// setInterval(function() {
//     document.getElementById('conf_oca1').checked = isChecked;
//     document.getElementById('conf_ocb1').checked = !isChecked;
//     isChecked = !isChecked;
// }, 2000);


// setInterval(function() {
//     var elements = document.getElementsByClassName('orange-text');

//     for (var i = 0; i < elements.length; i++) {
//         var randomValue = Math.floor(Math.random() * 100); // generates a random number between 0 and 99
//         elements[i].innerText = randomValue;
//     }
// }, 2000); // changes the value every 2 seconds

setInterval(function() {
    var tempoTesteElement = document.getElementById('tempo_teste');
    var currentValue = parseInt(tempoTesteElement.innerText);
    tempoTesteElement.innerText = currentValue + 1;
}, 1000); // increments the value every 1 second