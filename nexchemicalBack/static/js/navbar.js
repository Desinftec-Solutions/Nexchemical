// Global navbar: search toggle + full-screen mobile menu.
document.addEventListener('DOMContentLoaded', function () {
  var nav = document.querySelector('[data-navbar]');
  if (!nav) return;

  // --- search toggle ---
  var searchToggle = nav.querySelector('[data-search-toggle]');
  var searchInput = nav.querySelector('.nav__search input');
  if (searchToggle && searchInput) {
    searchToggle.addEventListener('click', function () {
      var open = nav.classList.toggle('nav--search-open');
      searchToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) searchInput.focus();
    });
  }

  // --- language dropdown ---
  var langDropdown = nav.querySelector('[data-lang-dropdown]');
  var langToggle = nav.querySelector('[data-lang-toggle]');
  if (langDropdown && langToggle) {
    var setLangOpen = function (open) {
      langDropdown.classList.toggle('is-open', open);
      langToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    };

    langToggle.addEventListener('click', function (e) {
      e.stopPropagation();
      setLangOpen(!langDropdown.classList.contains('is-open'));
    });

    document.addEventListener('click', function (e) {
      if (!langDropdown.contains(e.target)) setLangOpen(false);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') setLangOpen(false);
    });
  }

  // --- full-screen mobile menu ---
  var menuBtn = nav.querySelector('[data-menu-toggle]');
  var menu = document.querySelector('[data-nav-menu]');
  if (menuBtn && menu) {
    var setMenuOpen = function (open) {
      menu.classList.toggle('is-open', open);
      document.body.classList.toggle('nav-menu-open', open);
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    };

    menuBtn.addEventListener('click', function () {
      setMenuOpen(!menu.classList.contains('is-open'));
    });

    // Close on the X button or on any link inside the menu.
    menu.addEventListener('click', function (e) {
      if (e.target.closest('[data-menu-close]') || e.target.closest('a')) {
        setMenuOpen(false);
      }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.classList.contains('is-open')) {
        setMenuOpen(false);
      }
    });
  }
});
