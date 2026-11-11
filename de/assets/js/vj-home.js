/* Væringjar II — home page: header turns solid after the first screen; panels fade in. */
(function(){
  'use strict';
  var header=document.querySelector('.site-header');
  function onScroll(){ if(header) header.classList.toggle('vjc-solid', window.scrollY>40); }
  window.addEventListener('scroll', onScroll, {passive:true}); onScroll();
  var items=document.querySelectorAll('.vjc-reveal');
  if(!('IntersectionObserver' in window)){ items.forEach(function(e){e.classList.add('vjc-in');}); return; }
  var io=new IntersectionObserver(function(entries){
    entries.forEach(function(en){ if(en.isIntersecting){ en.target.classList.add('vjc-in'); io.unobserve(en.target); } });
  },{threshold:.18});
  items.forEach(function(e){ io.observe(e); });
})();
