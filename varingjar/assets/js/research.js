document.addEventListener('DOMContentLoaded', () => {
  const input = document.querySelector('[data-research-search]');
  const filters = [...document.querySelectorAll('[data-research-filter]')];
  const rows = [...document.querySelectorAll('[data-research-row]')];
  const empty = document.querySelector('[data-research-empty]');
  const count = document.querySelector('[data-research-count]');

  const normalize = value => (value || '')
    .toString()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9а-яіїєґ+.#-]+/gi, ' ')
    .trim();

  const haystack = row => normalize([
    row.dataset.search || '',
    row.textContent || '',
    row.dataset.type || ''
  ].join(' '));

  let type = 'all';

  function setFilter(next) {
    const exists = next === 'all' || filters.some(b => b.dataset.researchFilter === next);
    type = exists ? next : 'all';
    filters.forEach(btn => btn.classList.toggle('active', btn.dataset.researchFilter === type));
  }

  function apply() {
    const tokens = normalize(input?.value || '').split(' ').filter(Boolean);
    let shown = 0;

    rows.forEach(row => {
      const text = haystack(row);
      const okType = type === 'all' || row.dataset.type === type;
      const okText = tokens.every(token => text.includes(token));
      const visible = okType && okText;

      // Use both hidden and explicit display so author CSS can never override filtering.
      row.hidden = !visible;
      row.style.display = visible ? '' : 'none';
      row.setAttribute('aria-hidden', visible ? 'false' : 'true');
      if (visible) shown += 1;
    });

    if (empty) empty.style.display = shown ? 'none' : 'block';
    if (count) count.textContent = `${shown} ${shown === 1 ? 'record' : 'records'}`;
  }

  input?.addEventListener('input', apply);
  input?.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      input.value = '';
      apply();
      input.blur();
    }
  });

  filters.forEach(btn => btn.addEventListener('click', () => {
    setFilter(btn.dataset.researchFilter || 'all');
    apply();
  }));

  // Supports links such as research.html?filter=publication&q=survivability
  const params = new URLSearchParams(window.location.search);
  setFilter(params.get('filter') || 'all');
  if (input && params.get('q')) input.value = params.get('q');
  apply();
});
