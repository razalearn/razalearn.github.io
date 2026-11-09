/* Salmari Labs: small progressive enhancements. The site works fully without this file. */
(function () {
  // Highlight the table-of-contents entry for the section being read.
  var links = document.querySelectorAll('.toc a[href^="#"]');
  var toc = document.querySelector('.toc details');
  if (toc && window.matchMedia('(max-width: 959px)').matches) toc.open = false;
  if (!links.length || !('IntersectionObserver' in window)) return;
  var byId = {};
  links.forEach(function (a) { byId[decodeURIComponent(a.getAttribute('href').slice(1))] = a; });
  var visible = {};
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { visible[e.target.id] = e.isIntersecting; });
    var current = null;
    document.querySelectorAll('.prose section[id]').forEach(function (s) {
      if (!current && visible[s.id]) current = s.id;
    });
    if (!current) return;
    links.forEach(function (a) { a.classList.remove('active'); a.removeAttribute('aria-current'); });
    byId[current].classList.add('active');
    byId[current].setAttribute('aria-current', 'true');
  }, { rootMargin: '-80px 0px -55% 0px' });
  document.querySelectorAll('.prose section[id]').forEach(function (s) { if (byId[s.id]) observer.observe(s); });

  // Collapse the mobile table of contents after a choice.
  links.forEach(function (a) {
    a.addEventListener('click', function () {
      var d = a.closest('details');
      if (d && window.matchMedia('(max-width: 959px)').matches) d.open = false;
    });
  });
})();
