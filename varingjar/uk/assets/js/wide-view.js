/* Væringjar II — WIDE-VIEW retired 2026-10-28.
   The site is responsive on phones; the forced desktop viewport and the phone notice are gone.
   This file only clears the consent stored by the old notice, so phones that accepted it
   return to the normal mobile layout. */
(function () {
  'use strict';
  var KEY = 'varingjarWideView';
  try { localStorage.removeItem(KEY); } catch (e) {}
  try { sessionStorage.removeItem(KEY); } catch (e) {}
  try { document.cookie = KEY + '=;path=/;max-age=0'; } catch (e) {}
  document.documentElement.classList.remove('vj-wide-view');
})();
