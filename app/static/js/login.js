document.addEventListener('DOMContentLoaded', function() {
  const loginForm = document.querySelector('.login-form');

  if (loginForm) {
    loginForm.addEventListener('submit', function(e) {
      const username = this.elements['username'].value;
      const password = this.elements['password'].value;

      // Валидация полей
      if (!username || !password) {
        e.preventDefault();
        alert('Пожалуйста, заполните все поля');
        return false;
      }

      // Дополнительная логика при необходимости
      console.log('Попытка входа:', username);

      return true;
    });
  }
});