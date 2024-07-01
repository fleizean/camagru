document.getElementById('togglePassword').addEventListener('click', function () {
    const passwordField = document.getElementById('id_password');
    const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordField.setAttribute('type', type);
    this.textContent = type === 'password' ? 'Show' : 'Hide';
});

document.getElementById('change-profile').addEventListener('click', function() {
    const fileInput = document.getElementById('id_avatar');    
    fileInput.click(); // Dosya seçme dialogunu aç
});

document.getElementById('id_avatar').addEventListener('change', function(event) {
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('profile-img').src = e.target.result; // Seçilen fotoğrafı göster
    };
    reader.readAsDataURL(event.target.files[0]); // Dosyayı oku ve Data URL olarak dönüştür
});