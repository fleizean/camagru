document.getElementById('togglePassword').addEventListener('click', function () {
    const passwordField = document.getElementById('id_password');
    const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordField.setAttribute('type', type);
    this.textContent = type === 'password' ? 'Show' : 'Hide';
});
