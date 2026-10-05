(() => {
  'use strict';
  const intro = document.getElementById('liminal-intro');
  const page = document.getElementById('workspace-page');
  if (!intro || !page) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const copy = intro.querySelector('.intro-copy');
  const caption = intro.querySelector('.intro-caption');
  const robot = intro.querySelector('.intro-robot');
  const human = intro.querySelector('.intro-human');
  let state = 'active', scheduled = false, transitionFrame = null, transitionTimer = null;
  const clamp = n => Math.max(0, Math.min(1, n));
  const ease = n => n * n * (3 - 2 * n);
  function finish(focus = false) {
    if (state === 'awaiting' || state === 'released') return;
    state = reduced.matches ? 'released' : 'awaiting';
    if (transitionFrame) cancelAnimationFrame(transitionFrame);
    if (transitionTimer) window.clearTimeout(transitionTimer);
    document.body.classList.remove('intro-transitioning', 'intro-active');
    if (!reduced.matches) document.body.classList.add('intro-awaiting-scroll');
    intro.hidden = true;
    page.inert = false;
    page.removeAttribute('style');
    window.removeEventListener('scroll', schedule);
    window.removeEventListener('resize', schedule);
    reduced.removeEventListener('change', motionChanged);
    const query = new URLSearchParams(location.search);
    query.delete('intro');
    history.replaceState(null, '', '/workspace' + (query.toString() ? `?${query}` : ''));
    window.scrollTo(0, 0);
    if (focus || intro.contains(document.activeElement)) {
      const main = document.getElementById('main');
      main.setAttribute('tabindex', '-1');
      main.focus({preventScroll:true});
    }
  }
  function release(event) {
    if (state !== 'awaiting') return;
    if (event) event.preventDefault();
    state = 'released';
    document.body.classList.remove('intro-awaiting-scroll');
    document.body.style.removeProperty('overflow');
    window.removeEventListener('wheel', release, {capture:true});
    window.removeEventListener('touchstart', release, {capture:true});
    window.removeEventListener('keydown', release, {capture:true});
  }
  function beginTransition(focus = false) {
    if (state !== 'active') return;
    if (reduced.matches) { finish(focus); return; }
    state = 'transitioning';
    document.body.classList.add('intro-transitioning');
    document.body.style.overflow = 'hidden';
    transitionFrame = requestAnimationFrame(() => {
      transitionFrame = null;
      intro.style.opacity = '0';
      page.style.opacity = '1';
      page.style.transform = 'translateY(0px)';
      transitionTimer = window.setTimeout(() => finish(focus), 720);
    });
  }
  function frame() {
    scheduled = false;
    if (state !== 'active') return;
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
    // Let the transition own the final handoff so the workspace never snaps
    // to its completed state while the landing page is still scrolling.
    if (p >= .94) { beginTransition(); return; }
    intro.style.opacity = 1 - reveal;
    page.style.opacity = reveal;
    page.style.transform = `translateY(${22 * (1 - reveal)}px)`;
  }
  function schedule() { if (!scheduled && state === 'active') { scheduled = true; requestAnimationFrame(frame); } }
  function motionChanged() { if (reduced.matches && state === 'transitioning') finish(); }
  function bindEntryLinks() {
    intro.querySelectorAll('a[href="/workspace"]').forEach(link => link.addEventListener('click', event => {
      if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault(); beginTransition(true);
    }));
    const skip = document.querySelector('body > .skip');
    if (skip) skip.addEventListener('click', () => finish(true));
  }
  bindEntryLinks();
  if (reduced.matches) return; // Static scene, but entry links still transition in-place.
  document.body.classList.add('intro-active');
  page.inert = true;
  window.addEventListener('wheel', release, {passive:false, capture:true});
  window.addEventListener('touchstart', release, {passive:false, capture:true});
  window.addEventListener('keydown', release, {passive:false, capture:true});
  window.addEventListener('scroll', schedule, {passive:true});
  window.addEventListener('resize', schedule);
  reduced.addEventListener('change', motionChanged);
  schedule();
})();
