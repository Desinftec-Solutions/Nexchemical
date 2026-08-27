// Keeps the partner logo strip scrolling at a constant speed no matter
// how many logos are in the loop (duration is derived from measured width).
document.addEventListener('DOMContentLoaded', function () {
  var track = document.querySelector('[data-partners-track]');
  if (!track) return;

  var group = track.querySelector('.partners__group');
  if (!group) return;

  var PIXELS_PER_SECOND = 110;

  function setDuration() {
    var width = group.scrollWidth;
    if (width > 0) {
      track.style.animationDuration = (width / PIXELS_PER_SECOND) + 's';
    }
  }

  setDuration();
  window.addEventListener('load', setDuration);
  window.addEventListener('resize', setDuration);
});
