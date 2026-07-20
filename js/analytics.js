function loadAnalytics() {
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=G-ZRGR3F5RGX';
  document.head.appendChild(s);

  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag('js', new Date());
  gtag('config', 'G-ZRGR3F5RGX');

  var sb = document.createElement('script');
  sb.async = true;
  sb.src = 'https://cdn.splitbee.io/sb.js';
  document.head.appendChild(sb);
}

window.loadAnalytics = loadAnalytics;

if (localStorage.getItem('cookie-consent') === 'accepted') {
  loadAnalytics();
}
