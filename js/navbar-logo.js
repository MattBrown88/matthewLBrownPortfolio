document.addEventListener('DOMContentLoaded', function () {
  var brand = document.querySelector('.navbar-brand');
  if (!brand) return;
  var logo = document.createElement('a');
  logo.className = 'navbar-item navbar-logo';
  logo.href = '/';
  logo.setAttribute('aria-label', 'Home');
  logo.textContent = 'MB';
  brand.insertBefore(logo, brand.firstChild);
});
