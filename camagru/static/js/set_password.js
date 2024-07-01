document.getElementById('togglePassword').addEventListener('click', function () {
    const passwordField = document.getElementById('id_new_password1');
    const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordField.setAttribute('type', type);
    this.textContent = type === 'password' ? 'Show' : 'Hide';
});

document.getElementById('togglePassword2').addEventListener('click', function () {
    const passwordField = document.getElementById('id_new_password2');
    const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordField.setAttribute('type', type);
    this.textContent = type === 'password' ? 'Show' : 'Hide';
});
