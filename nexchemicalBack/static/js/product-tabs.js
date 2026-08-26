document.addEventListener('DOMContentLoaded', function () {
  var tabs = document.querySelectorAll('.tab[data-tab-target]');
  var panels = document.querySelectorAll('[data-tab-panel]');

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      var targetId = tab.getAttribute('data-tab-target');

      tabs.forEach(function (t) { t.classList.remove('tab--active'); });
      tab.classList.add('tab--active');

      panels.forEach(function (panel) {
        panel.hidden = panel.id !== targetId;
      });
    });
  });
});
