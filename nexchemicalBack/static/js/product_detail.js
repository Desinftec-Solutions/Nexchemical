document.addEventListener('DOMContentLoaded', function () {
  var tabButtons = document.querySelectorAll('.tab-btn');
  var panels = document.querySelectorAll('.tab-panel');

  tabButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var target = btn.getAttribute('data-tab');

      tabButtons.forEach(function (b) { b.classList.remove('is-active'); });
      panels.forEach(function (p) { p.classList.remove('is-active'); });

      btn.classList.add('is-active');
      var panel = document.getElementById(target);
      if (panel) {
        panel.classList.add('is-active');
      }
    });
  });
});
