/* Væringjar II · site navigator (2026-10-28).
   One panel on every page, desktop and phone: full-text search over all pages of the current
   language plus the complete site map with "you are here". Opened by the search button, the ☰
   button or the "/" key. Also folds section sidebars on phones so the article comes first.
   Data: assets/js/site-tree.js (always) and assets/js/site-search-<lang>.js (loaded on first search). */
(function () {
  'use strict';
  var script = document.currentScript;
  var ROOT = script ? script.src.replace(/assets\/js\/site-nav\.js.*$/, '') : '';
  var root = document.documentElement;
  var lang = (root.getAttribute('lang') || 'en').slice(0, 2).toLowerCase();
  if (lang !== 'uk' && lang !== 'de') lang = 'en';

  function ready(fn) { if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn); else fn(); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function norm(s) {
    return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
      .replace(/[’'ʼ`]/g, '').replace(/ё/g, 'е');
  }

  var T = (window.VJ_TREE || {})[lang];
  if (!T) return;
  var UI = T.ui;

  /* current page path relative to the language root */
  function currentPath() {
    var href = location.href.split('#')[0].split('?')[0];
    var rel = href.indexOf(ROOT) === 0 ? href.slice(ROOT.length) : '';
    rel = decodeURIComponent(rel);
    if (!rel || /\/$/.test(rel)) rel += 'index.html';
    if (T.p && rel.indexOf(T.p) === 0) rel = rel.slice(T.p.length);
    return rel;
  }
  var HERE = currentPath();

  function themeParam(url) {
    if (location.protocol !== 'file:') return url;
    var t = root.getAttribute('data-theme');
    if (t !== 'light' && t !== 'dark') return url;
    var parts = url.split('#');
    parts[0] += (parts[0].indexOf('?') >= 0 ? '&' : '?') + 'theme=' + t;
    return parts.join('#');
  }
  function href(u) { return themeParam(ROOT + T.p + u); }

  /* locate the current page in the tree */
  var trail = null;
  T.s.forEach(function (sec) {
    sec.i.forEach(function (n) {
      if (n.u === HERE) trail = [sec, n];
      (n.c || []).forEach(function (c) { if (c.u === HERE) trail = [sec, n, c]; });
    });
  });

  /* ---------------------------------------------------------------- panel */
  var panel, input, results, treeBox, lastFocus, searchLoaded = false, searchLoading = false;

  function treeHTML() {
    return T.s.map(function (sec) {
      var open = trail && trail[0] === sec;
      var items = sec.i.map(function (n) {
        var cur = n.u === HERE;
        var kids = (n.c || []).map(function (c) {
          var cc = c.u === HERE;
          return '<li><a href="' + esc(href(c.u)) + '"' + (cc ? ' aria-current="page" class="is-here"' : '') + '>' + esc(c.t) + '</a></li>';
        }).join('');
        return '<li><a href="' + esc(href(n.u)) + '"' + (cur ? ' aria-current="page" class="is-here"' : '') + '>' + esc(n.t) + '</a>' +
          (kids ? '<ul>' + kids + '</ul>' : '') + '</li>';
      }).join('');
      return '<details class="vjn-sec"' + (open ? ' open' : '') + '><summary>' + esc(sec.t) + '</summary><ul>' + items + '</ul></details>';
    }).join('');
  }

  function build() {
    if (panel) return;
    panel = document.createElement('div');
    panel.className = 'vjn';
    panel.id = 'vj-navigator';
    panel.hidden = true;
    var here = trail ? trail.map(function (x) { return esc(x.t); }).join(' <span aria-hidden="true">›</span> ') : '';
    panel.innerHTML =
      '<div class="vjn-backdrop" data-close></div>' +
      '<div class="vjn-panel" role="dialog" aria-modal="true" aria-labelledby="vjn-title">' +
        '<div class="vjn-head"><span id="vjn-title" class="vjn-title">' + esc(UI.title) + '</span>' +
          '<button type="button" class="vjn-close" data-close aria-label="' + esc(UI.close) + '">✕</button></div>' +
        (here ? '<p class="vjn-here"><span>' + esc(UI.here) + ':</span> ' + here + '</p>' : '') +
        '<label class="vjn-search"><span class="vjn-sr">' + esc(UI.search) + '</span>' +
          '<input type="search" autocomplete="off" spellcheck="false" placeholder="' + esc(UI.search) + '"></label>' +
        '<div class="vjn-results" aria-live="polite"></div>' +
        '<nav class="vjn-tree" aria-label="' + esc(UI.title) + '">' + treeHTML() + '</nav>' +
        '<p class="vjn-hint">' + esc(UI.hint) + '</p>' +
      '</div>';
    document.body.appendChild(panel);
    input = panel.querySelector('input');
    results = panel.querySelector('.vjn-results');
    treeBox = panel.querySelector('.vjn-tree');
    panel.addEventListener('click', function (e) { if (e.target.closest('[data-close]')) close(); });
    panel.addEventListener('keydown', onKey);
    var timer;
    input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(run, 110); });
    input.addEventListener('focus', loadSearch);
  }

  function open(focusSearch) {
    build();
    lastFocus = document.activeElement;
    panel.hidden = false;
    root.classList.add('vjn-lock');
    requestAnimationFrame(function () {
      panel.classList.add('is-open');
      if (focusSearch !== false) input.focus({ preventScroll: true });
      var cur = treeBox.querySelector('.is-here');
      if (cur && !input.value) cur.scrollIntoView({ block: 'center' });
    });
    document.querySelectorAll('.nav-toggle').forEach(function (b) { b.setAttribute('aria-expanded', 'true'); });
  }
  function close() {
    if (!panel || panel.hidden) return;
    panel.classList.remove('is-open');
    panel.hidden = true;
    root.classList.remove('vjn-lock');
    document.querySelectorAll('.nav-toggle').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
    if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
  }

  function onKey(e) {
    if (e.key === 'Escape') { e.preventDefault(); close(); return; }
    var links = Array.prototype.slice.call(results.querySelectorAll('a'));
    if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && links.length) {
      e.preventDefault();
      var i = links.indexOf(document.activeElement);
      i = e.key === 'ArrowDown' ? Math.min(links.length - 1, i + 1) : i - 1;
      if (i < 0) input.focus(); else links[i].focus();
    } else if (e.key === 'Enter' && document.activeElement === input && links.length) {
      e.preventDefault(); links[0].click();
    } else if (e.key === 'Tab') {
      var f = Array.prototype.slice.call(panel.querySelectorAll('button, input, summary, a[href]')).filter(function (el) { return el.offsetParent !== null; });
      if (!f.length) return;
      if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
      else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
    }
  }

  /* ---------------------------------------------------------------- search */
  var INDEX = null;
  function loadSearch() {
    if (searchLoaded || searchLoading) return;
    searchLoading = true;
    var s = document.createElement('script');
    s.src = ROOT + 'assets/js/site-search-' + lang + '.js?v=' + (script && script.src.split('?v=')[1] || '1');
    s.onload = function () {
      searchLoaded = true;
      INDEX = ((window.VJ_SEARCH || {})[lang] || []).map(function (e) {
        return { e: e, t: norm(e.t), d: norm(e.d), h: norm(e.h), x: norm(e.x) };
      });
      if (input.value) run();
    };
    document.head.appendChild(s);
  }

  function snippet(raw, tokens) {
    var n = norm(raw), at = -1, tok = '';
    tokens.forEach(function (t) { var p = n.indexOf(t); if (p >= 0 && (at < 0 || p < at)) { at = p; tok = t; } });
    if (at < 0) return esc(raw.slice(0, 160)) + (raw.length > 160 ? '…' : '');
    var a = Math.max(0, at - 70), b = Math.min(raw.length, at + tok.length + 110);
    var piece = raw.slice(a, b);
    var np = norm(piece), out = '', i = 0;
    while (i < piece.length) {
      var hit = null;
      for (var k = 0; k < tokens.length; k++) { if (tokens[k] && np.substr(i, tokens[k].length) === tokens[k]) { hit = tokens[k]; break; } }
      if (hit) { out += '<mark>' + esc(piece.substr(i, hit.length)) + '</mark>'; i += hit.length; }
      else { out += esc(piece[i]); i++; }
    }
    return (a > 0 ? '…' : '') + out + (b < raw.length ? '…' : '');
  }

  function run() {
    var q = input.value.trim();
    if (!q) { results.innerHTML = ''; treeBox.hidden = false; return; }
    treeBox.hidden = true;
    if (!INDEX) { loadSearch(); results.innerHTML = '<p class="vjn-status">…</p>'; return; }
    var tokens = norm(q).split(/[^a-z0-9а-яіїєґäöüß+#.-]+/i).filter(function (t) { return t.length > 1 || /\d/.test(t); });
    if (!tokens.length) { results.innerHTML = ''; return; }
    var hits = [], phrase = tokens.join(' ');
    function word(hay, t) { return new RegExp('(^|[^a-z0-9а-яіїєґäöüß])' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '($|[^a-z0-9а-яіїєґäöüß])').test(hay); }
    var idf = tokens.map(function (t) {
      var df = 0; INDEX.forEach(function (r) { if (r.t.indexOf(t) >= 0 || r.h.indexOf(t) >= 0 || r.x.indexOf(t) >= 0) df++; });
      return Math.log(1 + INDEX.length / (1 + df));
    });
    INDEX.forEach(function (r) {
      var score = 0;
      if (tokens.length > 1) {
        if (r.t.indexOf(phrase) >= 0) score += 40;
        if (r.h.indexOf(phrase) >= 0) score += 20;
        if (r.x.indexOf(phrase) >= 0) score += 14 + Math.min(10, 2 * (r.x.split(phrase).length - 2));
      }
      for (var i = 0; i < tokens.length; i++) {
        var t = tokens[i], s = 0;
        if (r.t.indexOf(t) >= 0) s += word(r.t, t) ? 14 : 6;
        if (r.h.indexOf(t) >= 0) s += word(r.h, t) ? 6 : 2;
        if (r.d.indexOf(t) >= 0) s += 3;
        if (r.x.indexOf(t) >= 0) s += (word(r.x, t) ? 2 : 1) + Math.min(4, r.x.split(t).length - 2);
        if (!s) return;
        score += s * idf[i];
      }
      hits.push({ r: r, s: score });
    });
    hits.sort(function (a, b) { return b.s - a.s; });
    if (!hits.length) { results.innerHTML = '<p class="vjn-status">' + esc(UI.none) + '</p>'; treeBox.hidden = false; return; }
    var first = q.split(/\s+/)[0];
    results.innerHTML = '<p class="vjn-status">' + hits.length + ' ' + esc(UI.results) + '</p><ol>' + hits.slice(0, 40).map(function (h) {
      var e = h.r.e;
      var inTitle = tokens.every(function (t) { return h.r.t.indexOf(t) >= 0; });
      var frag = tokens.length > 1 && h.r.x.indexOf(phrase) >= 0 ? q : first;
      var url = href(e.u) + (inTitle ? '' : '#:~:text=' + encodeURIComponent(frag));
      var src = h.r.x.indexOf(tokens[0]) >= 0 ? e.x : (e.d || e.h || e.x);
      return '<li><a href="' + esc(url) + '"><span class="vjn-r-sec">' + esc(e.s) + '</span><span class="vjn-r-title">' + esc(e.t) +
        '</span><span class="vjn-r-snip">' + snippet(src, tokens) + '</span></a></li>';
    }).join('') + '</ol>';
  }

  /* ---------------------------------------------------------------- header entry points */
  function mountHeader() {
    var nav = document.querySelector('.site-header .nav');
    if (nav && !nav.querySelector('.vjn-open')) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'vjn-open';
      b.setAttribute('aria-label', UI.open);
      b.setAttribute('title', UI.open + ' ( / )');
      b.innerHTML = '<svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5"/></svg><span>' + esc(UI.short) + '</span>';
      var anchor = nav.querySelector('.theme-toggle') || nav.querySelector('.lang-switch');
      if (anchor) nav.insertBefore(b, anchor); else nav.appendChild(b);
      b.addEventListener('click', function () { open(true); });
    }
    document.querySelectorAll('.nav-toggle').forEach(function (t) {
      t.setAttribute('aria-controls', 'vj-navigator');
      t.setAttribute('aria-label', UI.open);
    });
  }
  // The ☰ button opens the navigator instead of the old five-link dropdown.
  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('.nav-toggle');
    if (!t) return;
    e.preventDefault();
    e.stopPropagation();
    open(window.matchMedia('(min-width: 761px)').matches);
  }, true);
  document.addEventListener('keydown', function (e) {
    if (e.key !== '/' || e.ctrlKey || e.metaKey || e.altKey) return;
    var el = document.activeElement;
    if (el && (el.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName))) return;
    e.preventDefault();
    open(true);
  });

  /* ---------------------------------------------------------------- phone: fold section sidebars */
  function foldSidebars() {
    document.querySelectorAll('.research-sidebar').forEach(function (bar) {
      var inner = bar.querySelector('.research-sidebar-inner') || bar;
      if (inner.querySelector('.vjn-side-toggle')) return;
      var title = (bar.querySelector('.research-tree-title') || {}).textContent || UI.contents;
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'vjn-side-toggle';
      btn.setAttribute('aria-expanded', 'false');
      btn.innerHTML = '<span>' + esc(title) + '</span><b aria-hidden="true">▾</b>';
      inner.insertBefore(btn, inner.firstChild);
      btn.addEventListener('click', function () {
        var openNow = bar.classList.toggle('vjn-side-open');
        btn.setAttribute('aria-expanded', openNow ? 'true' : 'false');
      });
    });
  }

  ready(function () { mountHeader(); foldSidebars(); });
})();
