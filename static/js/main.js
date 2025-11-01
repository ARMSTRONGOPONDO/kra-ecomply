document.addEventListener('DOMContentLoaded', () => {
  const home = document.getElementById('home-intro');
  const login = document.getElementById('login-form');
  const showLoginBtn = document.getElementById('show-login-btn');
  const backHomeBtn = document.getElementById('back-home-btn');

  if (!home || !login) {
    console.error('Auth UI: home or login element not found', { home, login });
    return;
  }

  
  const showElement = (el) => {
    el.classList.remove('opacity-0', 'translate-x-6', 'pointer-events-none');
    el.classList.add('opacity-100', 'translate-x-0', 'pointer-events-auto');
  };


  const hideElement = (el) => {
    el.classList.add('opacity-0', 'translate-x-6', 'pointer-events-none');
    el.classList.remove('opacity-100', 'translate-x-0', 'pointer-events-auto');
  };


  if (showLoginBtn) {
    showLoginBtn.addEventListener('click', (e) => {
      e.preventDefault();
      hideElement(home);
   
      requestAnimationFrame(() => showElement(login));
    });
  }

 
  if (backHomeBtn) {
    backHomeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      hideElement(login);
      requestAnimationFrame(() => showElement(home));
    });
  }


  if (new URLSearchParams(window.location.search).get('login') === '1') {
    hideElement(home);
    showElement(login);
  }
});