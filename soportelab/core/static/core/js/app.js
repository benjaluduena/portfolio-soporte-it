(() => {
  const sidebar = document.querySelector('#sidebar');
  const sidebarToggles = document.querySelectorAll('[data-sidebar-toggle]');

  const closeSidebar = () => {
    if (!sidebar) return;
    sidebar.classList.remove('is-open');
    document.body.classList.remove('sidebar-open');
    sidebarToggles.forEach((button) => button.setAttribute('aria-expanded', 'false'));
  };

  sidebarToggles.forEach((button) => {
    button.addEventListener('click', () => {
      if (!sidebar) return;
      const willOpen = !sidebar.classList.contains('is-open');
      sidebar.classList.toggle('is-open', willOpen);
      document.body.classList.toggle('sidebar-open', willOpen);
      sidebarToggles.forEach((item) => item.setAttribute('aria-expanded', String(willOpen)));
    });
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeSidebar();
  });

  document.querySelectorAll('[data-dismiss]').forEach((button) => {
    button.addEventListener('click', () => button.closest('.alert')?.remove());
  });

  document.querySelectorAll('[data-password-toggle]').forEach((button) => {
    button.addEventListener('click', () => {
      const input = button.parentElement?.querySelector('input');
      if (!input) return;
      const reveal = input.type === 'password';
      input.type = reveal ? 'text' : 'password';
      button.textContent = reveal ? 'Ocultar' : 'Ver';
      button.setAttribute('aria-label', reveal ? 'Ocultar contraseña' : 'Mostrar contraseña');
    });
  });

  document.querySelectorAll('[data-dialog-open]').forEach((button) => {
    button.addEventListener('click', () => document.getElementById(button.dataset.dialogOpen)?.showModal());
  });

  document.querySelectorAll('[data-dialog-close]').forEach((button) => {
    button.addEventListener('click', () => button.closest('dialog')?.close());
  });

  document.querySelectorAll('[data-feedback]').forEach((button) => {
    button.addEventListener('click', () => {
      const container = button.closest('.article-feedback');
      if (container) container.innerHTML = '<strong>Gracias por tu respuesta.</strong>';
    });
  });
})();
