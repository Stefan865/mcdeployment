function sendData() {
    var form = document.getElementById("choicesForm");
    var formData = new FormData(form);
    var options = [];
    
    formData.getAll("option").forEach(option => {
        options.push(option);
    });

    var jsonData = JSON.stringify({ options: options });

    // Display the collected data (you can replace this with sending the data to a server)
    alert("Data collected:\n" + jsonData);
}

function toggleCheckbox(img) {
    var checkbox = img.previousElementSibling;
    checkbox.checked = !checkbox.checked;
}

function sendDataToServer() {
    var selectedServers = [];
    document.querySelectorAll('.server-image:checked').forEach(function(image) {
        selectedServers.push(image.alt);
    });
    var jsonData = JSON.stringify({ selectedServers: selectedServers });
    alert("Selected Servers:\n" + jsonData);
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
}


