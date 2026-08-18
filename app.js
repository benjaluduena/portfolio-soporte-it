(() => {
  const slides = [...document.querySelectorAll('.slide')];
  const previous = document.querySelector('#previousSlide');
  const next = document.querySelector('#nextSlide');
  const counter = document.querySelector('#slideCounter');
  const printButton = document.querySelector('#printPortfolio');
  const toolbar = document.querySelector('.preview-toolbar');
  let current = 0;
  let resizeFrame = 0;

  document.body.classList.add('js-ready');

  function fitPortfolio() {
    if (document.body.classList.contains('export-mode')) {
      document.documentElement.style.setProperty('--preview-scale', '1');
      return;
    }

    const toolbarHeight = toolbar?.getBoundingClientRect().height ?? 64;
    const availableWidth = Math.max(1, window.innerWidth - 32);
    const availableHeight = Math.max(1, window.innerHeight - toolbarHeight - 24);
    const scale = Math.min(1, availableWidth / 1080, availableHeight / 1350);
    document.documentElement.style.setProperty('--preview-scale', scale.toFixed(4));
  }

  function showSlide(index) {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, position) => {
      const active = position === current;
      slide.classList.toggle('is-active', active);
      slide.setAttribute('aria-hidden', active ? 'false' : 'true');
    });
    counter.textContent = `${current + 1} / ${slides.length}`;
    document.title = `${String(current + 1).padStart(2, '0')} · Resolver. Documentar. Prevenir.`;
  }

  previous?.addEventListener('click', () => showSlide(current - 1));
  next?.addEventListener('click', () => showSlide(current + 1));
  printButton?.addEventListener('click', () => window.print());

  document.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowRight' || event.key === 'PageDown') showSlide(current + 1);
    if (event.key === 'ArrowLeft' || event.key === 'PageUp') showSlide(current - 1);
    if (event.key.toLowerCase() === 'p' && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      window.print();
    }
  });

  const parameters = new URLSearchParams(window.location.search);
  if (parameters.get('export') === '1') document.body.classList.add('export-mode');
  const requested = Number(parameters.get('slide'));
  fitPortfolio();
  showSlide(Number.isFinite(requested) && requested > 0 ? requested - 1 : 0);

  window.addEventListener('resize', () => {
    window.cancelAnimationFrame(resizeFrame);
    resizeFrame = window.requestAnimationFrame(fitPortfolio);
  });
})();
