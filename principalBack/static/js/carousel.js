document.addEventListener('DOMContentLoaded', function () {
  var track = document.getElementById('carouselTrack');
  if (!track) {
    return;
  }

  var cards = Array.prototype.slice.call(track.querySelectorAll('.carousel__card'));
  var total = cards.length;
  if (total === 0) {
    return;
  }

  var config = getConfig(window.innerWidth);
  var position = Math.floor((total - 1) / 2);
  var dragging = false;
  var startX = 0;
  var startPosition = 0;
  var lastX = 0;
  var lastTime = 0;
  var velocity = 0;

  function getConfig(width) {
    if (width < 640) {
      return { sensitivity: 150, xMultiplier: 78, yMultiplier: 16, rotationMultiplier: 7, scaleReduction: 0.07, velocityDivisor: 500 };
    }
    if (width < 1024) {
      return { sensitivity: 200, xMultiplier: 130, yMultiplier: 26, rotationMultiplier: 9, scaleReduction: 0.08, velocityDivisor: 650 };
    }
    return { sensitivity: 230, xMultiplier: 160, yMultiplier: 34, rotationMultiplier: 10, scaleReduction: 0.1, velocityDivisor: 800 };
  }

  function clampPosition(p) {
    return Math.max(0, Math.min(total - 1, p));
  }

  function render(withTransition) {
    cards.forEach(function (card, i) {
      var offset = i - position;
      var absOffset = Math.abs(offset);
      var x = offset * config.xMultiplier;
      var rotate = absOffset < 0.05 ? 0 : offset * config.rotationMultiplier;
      var y = absOffset < 0.05 ? 0 : absOffset * config.yMultiplier;
      var scale = Math.max(0.72, 1 - absOffset * config.scaleReduction);
      var opacity = absOffset > 3.2 ? 0 : Math.max(0, 1 - Math.max(0, absOffset - 2.2) * 1.4);
      var z = Math.round(100 - absOffset * 10);

      card.style.transition = withTransition
        ? 'transform 0.45s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.3s ease'
        : 'none';
      card.style.transform = 'translateX(-50%) translate(' + x + 'px, ' + y + 'px) rotate(' + rotate + 'deg) scale(' + scale + ')';
      card.style.opacity = String(opacity);
      card.style.zIndex = String(z);
    });
  }

  function getClientX(e) {
    if (e.touches && e.touches.length) {
      return e.touches[0].clientX;
    }
    if (e.changedTouches && e.changedTouches.length) {
      return e.changedTouches[0].clientX;
    }
    return e.clientX;
  }

  function onPointerDown(e) {
    dragging = true;
    startX = getClientX(e);
    startPosition = position;
    lastX = startX;
    lastTime = Date.now();
    velocity = 0;
    track.classList.add('is-dragging');
  }

  function onPointerMove(e) {
    if (!dragging) {
      return;
    }
    var x = getClientX(e);
    var now = Date.now();
    var dt = now - lastTime || 16;
    velocity = ((x - lastX) / dt) * 1000;
    lastX = x;
    lastTime = now;

    var delta = (startX - x) / config.sensitivity;
    position = clampPosition(startPosition + delta);
    render(false);

    if (e.cancelable) {
      e.preventDefault();
    }
  }

  function onPointerUp() {
    if (!dragging) {
      return;
    }
    dragging = false;
    track.classList.remove('is-dragging');

    var velocityShift = -velocity / config.velocityDivisor;
    var target = clampPosition(Math.round(position + velocityShift));
    position = target;
    render(true);
  }

  track.addEventListener('mousedown', onPointerDown);
  window.addEventListener('mousemove', onPointerMove);
  window.addEventListener('mouseup', onPointerUp);

  track.addEventListener('touchstart', onPointerDown, { passive: true });
  window.addEventListener('touchmove', onPointerMove, { passive: false });
  window.addEventListener('touchend', onPointerUp);

  window.addEventListener('resize', function () {
    config = getConfig(window.innerWidth);
    render(false);
  });

  render(true);
});
