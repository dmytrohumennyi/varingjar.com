/* Only presentational sidebar filtering. No page content injection. */
(function () {
  'use strict';
  function init() {
    document.querySelectorAll('.research-sidebar').forEach(function (bar) {
      var search = bar.querySelector('.research-tree-search');
      if (!search) return;
      var links = Array.prototype.slice.call(bar.querySelectorAll('.research-tree-link'));
      search.addEventListener('input', function () {
        var query = search.value.toLocaleLowerCase().trim();
        links.forEach(function (link) {
          link.hidden = !!query && !link.textContent.toLocaleLowerCase().includes(query);
        });
        bar.querySelectorAll('.research-tree details').forEach(function (g) {
          if (query) g.open = true;
        });
      });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once:true});
  else init();
}());
