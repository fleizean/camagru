document.getElementById('file').addEventListener('change', function(e) {
    var fileName = e.target.files[0].name; // Get the name of the file
    document.getElementById("file_name_field").innerText = fileName; // Set the text content of the span to the file name
});

document.getElementById('togglePassword1').addEventListener('click', function () {
    const passwordField = document.getElementById('id_password1');
    const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordField.setAttribute('type', type);
    this.textContent = type === 'password' ? 'Show' : 'Hide';
});

document.getElementById('togglePassword2').addEventListener('click', function () {
    const passwordField = document.getElementById('id_password2');
    const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordField.setAttribute('type', type);
    this.textContent = type === 'password' ? 'Show' : 'Hide';
});


