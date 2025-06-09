document.addEventListener('DOMContentLoaded', function() {
  // Добавляем обработчики для пунктов меню
  const menuLinks = document.querySelectorAll('.menu-link');

  menuLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      // Добавляем анимацию при клике
      this.style.transform = 'translateY(0)';
      console.log('Переход по ссылке:', this.href);
    });

    link.addEventListener('mousedown', function() {
      this.style.transform = 'translateY(1px)';
    });

    link.addEventListener('mouseup', function() {
      this.style.transform = 'translateY(-2px)';
    });
  });

  // Обработчик для кнопки выхода
  const logoutBtn = document.querySelector('.logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', function(e) {
      if (!confirm('Вы уверены, что хотите выйти?')) {
        e.preventDefault();
      }
    });

    logoutBtn.addEventListener('mousedown', function() {
      this.style.transform = 'translateY(1px)';
    });

    logoutBtn.addEventListener('mouseup', function() {
      this.style.transform = 'translateY(-2px)';
    });
  }
});