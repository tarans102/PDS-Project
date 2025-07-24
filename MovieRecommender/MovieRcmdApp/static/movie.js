
window.addEventListener('scroll', function () {
    scrollTop = window.scrollY
    background.style.opacity = 2 - (scrollTop) / 200;
})
