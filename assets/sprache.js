// Language. Two kinds of pages:
// - Home page: one address per language (/ and /en/, linked via <link rel="alternate" hreflang>).
//   The language is fixed in <html lang>; the buttons switch the address. No redirect by browser
//   language, otherwise search engines (English browser) never see the German version. A language
//   picked once opens directly; without a choice, a bar offers the other version.
// - Other pages: stored choice, else browser language; texts (title included) from data-de / data-en.
(function () {
  function stored() { try { return localStorage.getItem('xharig.lang'); } catch (e) { return null; } }
  function keep(lang) { try { localStorage.setItem('xharig.lang', lang); } catch (e) { /* ohne Speicher nur für diese Sitzung */ } }
  var browser = ((navigator.languages && navigator.languages[0]) || navigator.language || 'de').toLowerCase().slice(0, 2) === 'de' ? 'de' : 'en';
  var choice = stored();
  if (choice !== 'de' && choice !== 'en') choice = null;
  var knoepfe = document.querySelectorAll('.sprache [data-lang]');

  var adresse = {};
  document.querySelectorAll('link[rel="alternate"][hreflang]').forEach(function (l) { adresse[l.hreflang] = new URL(l.href).pathname; });

  if (adresse.de && adresse.en) {
    var seite = document.documentElement.lang === 'en' ? 'en' : 'de';
    if (choice && choice !== seite) { location.replace(adresse[choice]); return; }
    knoepfe.forEach(function (k) {
      k.addEventListener('click', function (event) {
        event.preventDefault();
        keep(k.dataset.lang);
        if (k.dataset.lang !== seite) location.href = adresse[k.dataset.lang];
      });
    });
    if (!choice && browser !== seite) {
      var leiste = document.getElementById('hinweis-sprache');
      var link = document.getElementById('hinweis-sprache-link');
      var zu = document.getElementById('hinweis-sprache-zu');
      document.getElementById('hinweis-sprache-text').textContent = browser === 'en'
        ? 'This page is also available in English.' : 'Diese Seite gibt es auch auf Deutsch.';
      link.textContent = browser === 'en' ? 'English version →' : 'Zur deutschen Fassung →';
      link.href = adresse[browser];
      link.lang = browser;
      link.addEventListener('click', function () { keep(browser); });
      zu.setAttribute('aria-label', seite === 'de' ? 'Hinweis schließen' : 'Close notice');
      zu.title = zu.getAttribute('aria-label');
      zu.addEventListener('click', function () { keep(seite); leiste.hidden = true; });
      leiste.hidden = false;
    }
    return;
  }

  function set(lang, merken) {
    lang = lang === 'en' ? 'en' : 'de';
    document.documentElement.lang = lang;
    document.querySelectorAll('[data-de]').forEach(function (el) { el.textContent = el.dataset[lang]; });
    knoepfe.forEach(function (b) {
      var on = b.dataset.lang === lang;
      b.classList.toggle('an', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    if (merken) keep(lang);
  }
  knoepfe.forEach(function (b) {
    b.addEventListener('click', function () { set(b.dataset.lang, true); });
  });
  set(choice || browser, false);
})();
