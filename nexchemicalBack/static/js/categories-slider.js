// Pages the homepage category strip by one viewport-width at a time when
// there are more categories than fit on screen (see .category-slider--paged
// in style.css). The strip itself stays natively scrollable/swipeable even
// without this script — these buttons are just a discoverable shortcut.
document.addEventListener('DOMContentLoaded', function () {
  var track = document.querySelector('[data-category-track]');
  var prevBtn = document.querySelector('[data-category-prev]');
  var nextBtn = document.querySelector('[data-category-next]');
  if (!track || !prevBtn || !nextBtn) return;

  function updateButtons() {
    var maxScroll = track.scrollWidth - track.clientWidth;
    prevBtn.classList.toggle('category-slider__btn--disabled', track.scrollLeft <= 1);
    nextBtn.classList.toggle('category-slider__btn--disabled', track.scrollLeft >= maxScroll - 1);
  }

  prevBtn.addEventListener('click', function () {
    track.scrollBy({ left: -track.clientWidth, behavior: 'smooth' });
  });

  nextBtn.addEventListener('click', function () {
    track.scrollBy({ left: track.clientWidth, behavior: 'smooth' });
  });

  track.addEventListener('scroll', updateButtons, { passive: true });
  window.addEventListener('resize', updateButtons);
  updateButtons();
});
