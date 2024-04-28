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
    var form = document.getElementById("serversForm");
    var formData = new FormData(form);
    var servers = [];

    formData.getAll("server").forEach(server => {
        servers.push(server);
    });

    var jsonData = JSON.stringify({ servers: servers });

    // Display the collected data (you can replace this with sending the data to a server)
    alert("Selected Servers:\n" + jsonData);
}
