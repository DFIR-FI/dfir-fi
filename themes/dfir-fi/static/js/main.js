document.addEventListener('DOMContentLoaded', function () {
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('nav-links');

    hamburger.addEventListener('click', function () {
        const open = navLinks.classList.toggle('active');
        hamburger.setAttribute('aria-expanded', open);
    });
});
