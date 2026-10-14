// Sprache: gespeicherte Wahl, sonst Browsersprache. Texte (auch der Seitentitel) stehen in data-de / data-en.
(function () {
  function stored() { try { return localStorage.getItem('xharig.lang'); } catch (e) { return null; } }
  function set(lang, keep) {
    lang = lang === 'en' ? 'en' : 'de';
    document.documentElement.lang = lang;
    document.querySelectorAll('[data-de]').forEach(function (el) { el.textContent = el.dataset[lang]; });
    document.querySelectorAll('.sprache button').forEach(function (b) {
      var on = b.dataset.lang === lang;
      b.classList.toggle('an', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    if (keep) { try { localStorage.setItem('xharig.lang', lang); } catch (e) { /* ohne Speicher nur für diese Sitzung */ } }
  }
  document.querySelectorAll('.sprache button').forEach(function (b) {
    b.addEventListener('click', function () { set(b.dataset.lang, true); });
  });
  var first = stored() || ((navigator.languages && navigator.languages[0]) || navigator.language || 'de').toLowerCase().slice(0, 2);
  set(first, false);
})();
