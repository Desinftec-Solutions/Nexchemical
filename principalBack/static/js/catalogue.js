document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.getElementById('filterToggle');
  var panel = document.getElementById('filterPanel');

  if (toggle && panel) {
    toggle.addEventListener('click', function () {
      panel.classList.toggle('is-open');
    });

    if (panel.querySelector('.filter-pill.is-active')) {
      panel.classList.add('is-open');
    }
  }
});
