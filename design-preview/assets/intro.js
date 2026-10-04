(() => {
  'use strict';
  const intro = document.getElementById('liminal-intro');
  const page = document.getElementById('workspace-page');
  if (!intro || !page) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  if (reduced.matches) return; // Static scene and ordinary links; no scroll interception.
  const copy = intro.querySelector('.intro-copy');
  const caption = intro.querySelector('.intro-caption');
  const robot = intro.querySelector('.intro-robot');
  const human = intro.querySelector('.intro-human');
  let finished = false, scheduled = false;
  const clamp = n => Math.max(0, Math.min(1, n));
  const ease = n => n * n * (3 - 2 * n);
  function finish(focus = false) {
    if (finished) return;
    finished = true;
    document.body.classList.remove('intro-active');
    intro.hidden = true;
    page.inert = false;
    page.removeAttribute('style');
    window.removeEventListener('scroll', schedule);
    window.removeEventListener('resize', schedule);
    reduced.removeEventListener('change', motionChanged);
    history.replaceState(null, '', '/workspace' + location.search);
    window.scrollTo(0, 0);
    if (focus || intro.contains(document.activeElement)) {
      const main = document.getElementById('main');
      main.setAttribute('tabindex', '-1');
      main.focus({preventScroll:true});
    }
  }
  function frame() {
    scheduled = false;
    if (finished) return;
    const distance = document.querySelector('.intro-distance').offsetHeight - innerHeight;
    const p = clamp(scrollY / Math.max(1, distance));
    const approach = ease(clamp(p / .76));
    // Both tips share one image plane: x=48.8% and x=53.1%.
    robot.style.transform = `translateX(${-6 + 8.15 * approach}%)`;
    human.style.transform = `translateX(${6 - 8.15 * approach}%)`;
    const fade = 1 - ease(clamp(p / .56));
    copy.style.opacity = fade;
    copy.style.transform = `translateY(${-28 * (1 - fade)}px)`;
    caption.style.opacity = 1 - ease(clamp(p / .45));
    const reveal = ease(clamp((p - .80) / .19));
    intro.style.opacity = 1 - reveal;
    page.style.opacity = reveal;
    page.style.transform = `translateY(${22 * (1 - reveal)}px)`;
    if (p >= .99) finish();
  }
  function schedule() { if (!scheduled && !finished) { scheduled = true; requestAnimationFrame(frame); } }
  function motionChanged() { if (reduced.matches) finish(); }
  document.body.classList.add('intro-active');
  page.inert = true;
  intro.querySelectorAll('a[href="/workspace"]').forEach(link => link.addEventListener('click', event => {
    if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault(); finish(true);
  }));
  const skip = document.querySelector('body > .skip');
  if (skip) skip.addEventListener('click', () => finish(true));
  window.addEventListener('scroll', schedule, {passive:true});
  window.addEventListener('resize', schedule);
  reduced.addEventListener('change', motionChanged);
  schedule();
})();
