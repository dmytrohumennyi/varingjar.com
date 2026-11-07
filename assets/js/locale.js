(function(){
'use strict';
var SUP=['en','uk','de'];
function current(){
  var l=(document.documentElement.getAttribute('lang')||'en').toLowerCase();
  if(l.indexOf('uk')===0)return'uk';
  if(l.indexOf('de')===0)return'de';
  return'en';
}
function valid(x){return SUP.indexOf(x)>=0;}
function save(lang){
  try{localStorage.setItem('varingjarLanguage',lang);}catch(e){}
  try{document.cookie='varingjarLanguage='+lang+'; path=/; max-age=31536000; SameSite=Lax';}catch(e){}
}
function load(){
  try{var x=localStorage.getItem('varingjarLanguage');if(valid(x))return x;}catch(e){}
  try{var m=document.cookie.match(/(?:^|;\s*)varingjarLanguage=(en|uk|de)(?:;|$)/);return m?m[1]:null;}catch(e){return null;}
}
function anchor(lang){return document.querySelector('.lang-switch a[data-lang="'+lang+'"]');}
function go(lang,replace){
  if(!lang||lang===current()) return;
  var a=anchor(lang); if(!a) return;
  if(replace) location.replace(a.href); else location.assign(a.href);
}
document.querySelectorAll('.lang-switch a[data-lang]').forEach(function(a){
  a.addEventListener('click',function(){
    var lang=a.getAttribute('data-lang');
    if(valid(lang))save(lang);
  });
});
var q=null;try{q=new URLSearchParams(location.search).get('lang');}catch(e){}
if(valid(q)){
  save(q);
  if(q!==current()){go(q,true);return;}
  try{var u=new URL(location.href);u.searchParams.delete('lang');history.replaceState(null,'',u.pathname+u.search+u.hash);}catch(e){}
  return;
}
var pref=load();if(pref){go(pref,true);return;}
if(current()!=='en' || !/^https?:$/.test(location.protocol)) return;
fetch('/cdn-cgi/trace',{cache:'no-store'}).then(function(r){return r.ok?r.text():'';}).then(function(t){
  var m=t.match(/(?:^|\n)loc=([A-Z]{2})(?:\n|$)/);if(!m)return;var c=m[1];
  if(c==='UA')go('uk',true); else if(['DE','AT','CH','LI'].indexOf(c)>=0)go('de',true);
}).catch(function(){});
})();
