// Catalog page: toggles the filter/sort panel open and closed.
document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.getElementById('filterToggle');
  var panel = document.getElementById('filterPanel');

  if (!toggle || !panel) return;

  var setOpen = function (open) {
    panel.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  };

  toggle.addEventListener('click', function () {
    setOpen(!panel.classList.contains('is-open'));
  });

  // Keep the panel open on load if a filter or sort is already active.
  if (panel.classList.contains('filter-panel--has-active')) {
    setOpen(true);
  }
});
