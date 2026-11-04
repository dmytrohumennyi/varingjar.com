(function(){
'use strict';
var SUP=['en','uk','de'];
function current(){var p=location.pathname; if(/^\/uk(?:\/|$)/.test(p))return'uk'; if(/^\/de(?:\/|$)/.test(p))return'de'; return'en';}
function basePath(){return location.pathname.replace(/^\/(uk|de)(?=\/)/,'')||'/';}
function urlFor(lang){var p=basePath(); if(lang==='en') return p+location.search+location.hash; return '/'+lang+(p==='/'?'/':p)+location.search+location.hash;}
function save(lang){try{localStorage.setItem('varingjarLanguage',lang);}catch(e){}}
function load(){try{var x=localStorage.getItem('varingjarLanguage');return SUP.indexOf(x)>=0?x:null;}catch(e){return null;}}
function go(lang){if(lang&&lang!==current()) location.replace(urlFor(lang));}
var q=null; try{q=new URLSearchParams(location.search).get('lang');}catch(e){}
if(SUP.indexOf(q)>=0){save(q);go(q);return;}
document.querySelectorAll('.lang-switch a[data-lang]').forEach(function(a){a.addEventListener('click',function(){save(a.getAttribute('data-lang'));});});
var pref=load(); if(pref){go(pref);return;}
if(current()!=='en') return; // direct localized URL is respected
var bl=((navigator.languages&&navigator.languages[0])||navigator.language||'').toLowerCase();
if(/^uk(?:-|$)/.test(bl)){go('uk');return;} if(/^de(?:-|$)/.test(bl)){go('de');return;}
// Region fallback when browser language is not one of the supported languages.
fetch('/cdn-cgi/trace',{cache:'no-store'}).then(function(r){return r.ok?r.text():'';}).then(function(t){
 var m=t.match(/(?:^|\n)loc=([A-Z]{2})(?:\n|$)/); if(!m)return; var c=m[1];
 if(c==='UA')go('uk'); else if(['DE','AT','CH','LI'].indexOf(c)>=0)go('de');
}).catch(function(){});
})();
