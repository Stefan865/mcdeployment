function sendData() {
    // Get selected values
        var selectedOptions = {
            user_id: document.getElementById("user_id").value,
            tier: document.getElementById("tiers").value,
            level_seed: document.querySelector('input[name="option"]:nth-of-type(2)').value,
            gamemode: document.querySelector('input[name="option0"]:checked').value,
            motd: document.querySelector('input[name="option1"]').value,
            pvp: document.querySelector('input[name="option4"]:checked').value,
            generate_structures: document.querySelector('input[name="option8"]:checked').value,
            difficulty: document.querySelector('input[name="option2"]:checked').value,
            max_players: document.querySelector('select[name="option5"]').value,
            online_mode: document.querySelector('input[name="option3"]:checked').value,
            view_distance: document.querySelector('select[name="option6"]').value,
            hardcore: document.querySelector('input[name="option7"]:checked').value
           
        };

    var jsonData = JSON.stringify(selectedOptions);

    console.log("Selected Options (JSON):", jsonData);
    
    var apiUrl = 'https://7rirapp9nk.execute-api.eu-central-1.amazonaws.com/test1/CreateServer';

    // Send the JSON data to the API Gateway
    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // 'x-api-key': 'YOUR_API_KEY' // Uncomment this line if your API requires an API key
        },
        body: jsonData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
       // Send JSON data to server or do whatever you need with it
}
function showDropdown() {
    document.getElementById("numberDropdown").style.display = "block";
}

function hideDropdown() {
    document.getElementById("numberDropdown").style.display = "none";
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


