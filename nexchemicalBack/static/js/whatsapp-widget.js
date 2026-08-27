// Bottom-right WhatsApp widget: opens/closes a small panel (not live chat).
document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.getElementById('whatsappToggle');
  var panel = document.getElementById('whatsappPanel');
  var closeBtn = panel && panel.querySelector('[data-whatsapp-close]');

  if (!toggle || !panel) return;

  var setOpen = function (open) {
    panel.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  };

  toggle.addEventListener('click', function () {
    setOpen(!panel.classList.contains('is-open'));
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', function () {
      setOpen(false);
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') setOpen(false);
  });
});
