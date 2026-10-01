document.addEventListener('DOMContentLoaded', function () {
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('nav-links');

    hamburger.addEventListener('click', function () {
        const open = navLinks.classList.toggle('active');
        hamburger.setAttribute('aria-expanded', open);
    });
});

// Sister-site links: short glitch-out, then navigate in the same tab.
// Modified clicks (new tab/window) and reduced motion skip the effect.
const SISTER_DELAY_MS = 320;

document.addEventListener('click', function (e) {
    const link = e.target.closest('a[data-sister]');
    if (!link || e.defaultPrevented || e.button !== 0 ||
        e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) {
        return;
    }
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }
    e.preventDefault();
    document.documentElement.classList.add('leaving');
    setTimeout(function () {
        window.location.href = link.href;
    }, SISTER_DELAY_MS);
});

// Coming back with the back button restores the page from cache:
// drop the glitch-out state so the page isn't left covered.
window.addEventListener('pageshow', function (e) {
    if (e.persisted) {
        document.documentElement.classList.remove('leaving');
    }
});
