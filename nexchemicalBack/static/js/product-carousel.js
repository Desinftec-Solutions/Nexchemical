document.addEventListener('DOMContentLoaded', function () {
  var root = document.querySelector('[data-carousel-root]');
  if (!root) return;

  var surface = root.querySelector('[data-carousel-surface]');
  var cards = Array.prototype.slice.call(root.querySelectorAll('[data-carousel-card]'));
  var total = cards.length;
  if (!surface || !total) return;

  // Cards sit on the circumference of a circle of the given radius, spaced
  // angleStep degrees apart (see render()) — radius is the knob to tune
  // against the design: bigger = flatter arc, smaller = more pronounced bow.
  function getConfig(width) {
    if (width < 640) {
      return {
        distanceDivisor: 120, velocityDivisor: 500, sensitivity: 180,
        radius: 820, angleStep: 10, scaleReduction: 0.06
      };
    }
    if (width < 1024) {
      return {
        distanceDivisor: 160, velocityDivisor: 650, sensitivity: 220,
        radius: 980, angleStep: 11, scaleReduction: 0.09
      };
    }
    return {
      distanceDivisor: 200, velocityDivisor: 800, sensitivity: 250,
      radius: 1150, angleStep: 12, scaleReduction: 0.12
    };
  }

  var config = getConfig(window.innerWidth);
  window.addEventListener('resize', function () {
    config = getConfig(window.innerWidth);
    render();
  });

  var progress = 0;
  var target = 0;
  var springVelocity = 0;
  var dragging = false;
  var dragStartProgress = 0;
  var pointerStartX = 0;
  var lastX = 0;
  var lastT = 0;
  var pointerVelocity = 0;
  var animFrame = null;
  var hoveredCard = null;
  var HOVER_LIFT = 14;

  function clamp(value, lo, hi) { return Math.min(hi, Math.max(lo, value)); }

  function lerp(x, x0, x1, y0, y1) {
    if (x1 === x0) return y0;
    var t = clamp((x - x0) / (x1 - x0), 0, 1);
    return y0 + t * (y1 - y0);
  }

  function piecewise(x, xs, ys) {
    if (x <= xs[0]) return ys[0];
    if (x >= xs[xs.length - 1]) return ys[ys.length - 1];
    for (var i = 0; i < xs.length - 1; i++) {
      if (x >= xs[i] && x <= xs[i + 1]) return lerp(x, xs[i], xs[i + 1], ys[i], ys[i + 1]);
    }
    return ys[ys.length - 1];
  }

  function wrappedDiff(index, p) {
    var diff = (index - p) % total;
    if (diff > total / 2) diff -= total;
    if (diff < -total / 2) diff += total;
    return diff;
  }

  // Tracks each card's diff from the previous render, so a wrap (the
  // leftmost card's diff jumping straight to the rightmost, or vice versa)
  // can be told apart from ordinary continuous movement — see render().
  var lastDiff = {};

  function render() {
    for (var i = 0; i < cards.length; i++) {
      var card = cards[i];
      var index = parseInt(card.getAttribute('data-index'), 10);
      var diff = wrappedDiff(index, progress);
      var absDiff = Math.abs(diff);

      // Place the card on the circumference of a circle: one angle, scaled
      // by distance from center, drives x/y/rotate together so they stay
      // geometrically consistent (a real arc, not three independent ramps).
      var angleDeg = diff * config.angleStep;
      var angleRad = angleDeg * Math.PI / 180;
      var x = config.radius * Math.sin(angleRad);
      var y = config.radius * (1 - Math.cos(angleRad));
      var rotate = absDiff < 0.05 ? 0 : angleDeg;
      if (card === hoveredCard) y -= HOVER_LIFT;
      var scale = 1 - absDiff * config.scaleReduction;
      var opacity = piecewise(
        diff,
        [-total / 2, -total / 2 + 0.5, 0, total / 2 - 0.5, total / 2],
        [0, 1, 1, 1, 0]
      );
      var zIndex = Math.round(100 - absDiff * 10) + (card === hoveredCard ? 20 : 0);

      // wrappedDiff jumps a card's diff by a full lap almost instantly at
      // the wrap point. Without this, the CSS transition on transform
      // smoothly (and visibly) slides the card all the way across the
      // stage instead of it just reappearing, already faded out, on the
      // opposite side. Cards are invisible right at the wrap (opacity 0
      // there), so snapping the transform with no transition for that one
      // frame is unseen — it only reappears once opacity fades back in.
      var previousDiff = lastDiff[index];
      var wrapped = previousDiff !== undefined && Math.abs(diff - previousDiff) > total / 2;
      lastDiff[index] = diff;

      if (wrapped) card.style.transition = 'none';

      card.style.transform =
        'translate(-50%, -50%) translateX(' + x + 'px) translateY(' + y + 'px) ' +
        'rotate(' + rotate + 'deg) scale(' + scale + ')';
      card.style.opacity = String(opacity);
      card.style.zIndex = String(zIndex);

      if (wrapped) {
        // Flush the "none" transition and the snapped position within the
        // same frame, then hand back to the CSS transition for whatever
        // comes next.
        void card.offsetHeight;
        card.style.transition = '';
      }
    }
  }

  function findCardAtPoint(clientX, clientY) {
    var best = null;
    var bestZ = -Infinity;
    for (var i = 0; i < cards.length; i++) {
      var rect = cards[i].getBoundingClientRect();
      if (clientX >= rect.left && clientX <= rect.right && clientY >= rect.top && clientY <= rect.bottom) {
        var z = parseInt(cards[i].style.zIndex || '0', 10);
        if (z > bestZ) { bestZ = z; best = cards[i]; }
      }
    }
    return best;
  }

  function setHoveredCard(card) {
    if (card === hoveredCard) return;
    hoveredCard = card;
    render();
  }

  function stepSpring() {
    var stiffness = 200, damping = 30, mass = 1, dt = 1 / 60;
    var displacement = progress - target;
    var accel = (-stiffness * displacement - damping * springVelocity) / mass;
    springVelocity += accel * dt;
    progress += springVelocity * dt;
    render();

    if (Math.abs(displacement) > 0.001 || Math.abs(springVelocity) > 0.001) {
      animFrame = requestAnimationFrame(stepSpring);
    } else {
      progress = target;
      springVelocity = 0;
      render();
      animFrame = null;
    }
  }

  function animateTo(value) {
    target = value;
    if (animFrame) cancelAnimationFrame(animFrame);
    animFrame = requestAnimationFrame(stepSpring);
  }

  function onPointerDown(e) {
    dragging = true;
    setHoveredCard(null);
    if (animFrame) { cancelAnimationFrame(animFrame); animFrame = null; }
    dragStartProgress = progress;
    pointerStartX = e.clientX;
    lastX = e.clientX;
    lastT = performance.now();
    pointerVelocity = 0;
    if (surface.setPointerCapture) {
      try { surface.setPointerCapture(e.pointerId); } catch (err) { /* no-op */ }
    }
  }

  function onPointerMove(e) {
    if (!dragging) {
      setHoveredCard(findCardAtPoint(e.clientX, e.clientY));
      return;
    }
    var now = performance.now();
    var dx = e.clientX - lastX;
    var dt = Math.max(1, now - lastT);
    pointerVelocity = (dx / dt) * 1000;
    progress += -dx / config.sensitivity;
    lastX = e.clientX;
    lastT = now;
    render();
  }

  function onPointerUp(e) {
    if (!dragging) return;
    dragging = false;
    var dragDistance = e.clientX - pointerStartX;
    var distanceShift = -dragDistance / config.distanceDivisor;
    var velocityShift = -pointerVelocity / config.velocityDivisor;
    var totalShift = Math.round(distanceShift + velocityShift);
    totalShift = clamp(totalShift, -3, 3);
    animateTo(Math.round(dragStartProgress) + totalShift);
  }

  surface.addEventListener('pointerdown', onPointerDown);
  surface.addEventListener('pointermove', onPointerMove);
  surface.addEventListener('pointerup', onPointerUp);
  surface.addEventListener('pointercancel', onPointerUp);
  surface.addEventListener('pointerleave', function () { setHoveredCard(null); });

  render();
});
