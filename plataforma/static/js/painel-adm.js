document.addEventListener('DOMContentLoaded', () => {
    const adminNavigation = document.querySelector('.admin-navigation');
    const adminToggle = document.querySelector('.admin-toggle');

    adminToggle.addEventListener('click', () => {
        adminNavigation.classList.toggle('active');
    });
});