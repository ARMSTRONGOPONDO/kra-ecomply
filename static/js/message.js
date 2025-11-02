  setTimeout(() => {
    const messages = document.getElementById('flash-messages');
    if (messages) {
      messages.style.opacity = '0';
      setTimeout(() => messages.remove(), 500); // remove after fade-out
    }
  }, 3000);