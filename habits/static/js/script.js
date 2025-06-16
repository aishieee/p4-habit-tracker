// Toggle side bar
document.addEventListener('DOMContentLoaded', function () {
    const toggleButton = document.getElementById('menu-toggle');
    const wrapper = document.getElementById('wrapper');

    toggleButton.addEventListener('click', function () {
        wrapper.classList.toggle('toggled');
    });
});
