// Generic horizontal-scroll slider: wires up prev/next buttons for any
// [data-slider] root wrapping a [data-slider-track] (a native, natively
// swipeable overflow-x/scroll-snap element) and, optionally,
// [data-slider-prev] / [data-slider-next] buttons. The track stays usable
// via touch/trackpad scroll even without this script — the buttons are a
// discoverable shortcut on top of that.
//
// A root can also opt into data-slider-feature-last: the track's last
// fully-visible child gets an "is-featured" class, re-evaluated on every
// scroll/resize, so a card can grow (e.g. an unclamped two-line title —
// see .highlight-card / .highlight-card__title in style.css) only while it
// sits in that rightmost slot, then shrink back once scrolled past.
//
// Used by the homepage categories strip and the About section's highlight
// cards.
document.addEventListener('DOMContentLoaded', function () {
  var sliders = document.querySelectorAll('[data-slider]');

  sliders.forEach(function (slider) {
    var track = slider.querySelector('[data-slider-track]');
    if (!track) return;

    var prevBtn = slider.querySelector('[data-slider-prev]');
    var nextBtn = slider.querySelector('[data-slider-next]');

    if (prevBtn && nextBtn) {
      var updateButtons = function () {
        var maxScroll = track.scrollWidth - track.clientWidth;
        prevBtn.classList.toggle('slider-btn--disabled', track.scrollLeft <= 1);
        nextBtn.classList.toggle('slider-btn--disabled', track.scrollLeft >= maxScroll - 1);
      };

      prevBtn.addEventListener('click', function () {
        track.scrollBy({ left: -track.clientWidth, behavior: 'smooth' });
      });
      nextBtn.addEventListener('click', function () {
        track.scrollBy({ left: track.clientWidth, behavior: 'smooth' });
      });
      track.addEventListener('scroll', updateButtons, { passive: true });
      window.addEventListener('resize', updateButtons);
      updateButtons();
    }

    if ('sliderFeatureLast' in slider.dataset) {
      var items = track.children;

      var updateFeatured = function () {
        // getBoundingClientRect() is always viewport-relative regardless of
        // positioning context, unlike offsetLeft/offsetWidth (relative to
        // the nearest *positioned* ancestor — with none in this tree, that
        // silently resolves all the way up to <body>, not the track).
        var trackRight = track.getBoundingClientRect().right;
        var featured = items[items.length - 1];
        for (var i = 0; i < items.length; i++) {
          if (items[i].getBoundingClientRect().right <= trackRight + 1) {
            featured = items[i];
          }
        }
        for (var j = 0; j < items.length; j++) {
          items[j].classList.toggle('is-featured', items[j] === featured);
        }
      };

      track.addEventListener('scroll', updateFeatured, { passive: true });
      window.addEventListener('resize', updateFeatured);
      updateFeatured();
    }
  });
});
