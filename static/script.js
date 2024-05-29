function sendData() {
    // Get selected values
    var selectedOptions = {
        tier: document.getElementById("tiers").value,
        gameMode: document.querySelector('input[name="option"]:checked').value,
        gameModeType: document.querySelector('input[name="option1"]:checked').value
    };

    // Convert to JSON
    var jsonData = JSON.stringify(selectedOptions);

    // Display JSON in console (you can remove this line in production)
    console.log("Selected Options (JSON):", jsonData);

    // Send JSON data to server or do whatever you need with it
}


function toggleButton(image) {

}

function sendDataToServer() {
    var selectedServers = [];
    document.querySelectorAll('input[name="server"]:checked').forEach(function(checkbox) {
        selectedServers.push(checkbox.value);
    });
    

        localStorage.setItem('selectedServers', JSON.stringify(selectedServers));

    window.location.href = "/server_settings";
    

}

let lastClickedButton = null;

function toggleButton(button) {
    if (lastClickedButton) {
        lastClickedButton.disabled = false; // Enable the previously clicked button
        lastClickedButton.classList.remove('grayed-out'); // Remove the 'grayed-out' class
    }
    
    button.disabled = true; // Disable the newly clicked button
    button.classList.add('grayed-out'); // Add the 'grayed-out' class
    
    lastClickedButton = button; // Update the last clicked button
    document.querySelectorAll('.server-image:checked').forEach(function(image) {
        image.checked = false;
    });

    // Enable the clicked button
    button.disabled = true;
    button.classList.add('grayed-out');

    // Disable other buttons
    document.querySelectorAll('.server-image').forEach(function(image) {
        if (image !== button) {
            image.disabled = false;
            image.classList.remove('grayed-out');
        }
    });

}


