/* THEME-10/11: persistent presentation state, with storage/cookie and URL fallback.
   The stored selection wins; the URL is a fallback for file:// and blocked storage. */
(function(){
  'use strict';
  var KEY='varingjarTheme', COOKIE='varingjarTheme';
  var root=document.documentElement;
  var fallbackTransport=false;
  function valid(value){return value==='light'||value==='dark';}
  function cookieRead(){
    try {var match=document.cookie.match(/(?:^|;\s*)varingjarTheme=(light|dark)(?:;|$)/);return match?match[1]:null;}
    catch(_){return null;}
  }
  function storageRead(){
    try {var saved=localStorage.getItem(KEY);return valid(saved)?saved:null;}
    catch(_){fallbackTransport=true;return null;}
  }
  function urlRead(){
    try {var value=new URL(location.href).searchParams.get('theme');return valid(value)?value:null;}
    catch(_){return null;}
  }
  function chosen(){
    var stored=storageRead(), fromCookie=cookieRead(), fromUrl=urlRead();
    // An explicit URL value is used only when browser storage is unavailable,
    // on file: previews, or when no persisted setting exists.
    if(fromUrl&&(location.protocol==='file:'||fallbackTransport||(!stored&&!fromCookie)))return fromUrl;
    return stored||fromCookie||fromUrl||'dark';
  }
  function store(next){
    try {localStorage.setItem(KEY,next);}catch(_){fallbackTransport=true;}
    try {document.cookie=COOKIE+'='+next+'; path=/; max-age=31536000; SameSite=Lax';}catch(_){}
    // In file:// the URL is the reliable cross-document transport; never rewrite
    // a remote URL just to preserve a preference that storage already handles.
    if(location.protocol==='file:'||fallbackTransport){
      try {var u=new URL(location.href);u.searchParams.set('theme',next);history.replaceState(null,'',u.href);}catch(_){}
    }
  }
  function transportLinks(next){
    if(!(location.protocol==='file:'||fallbackTransport))return;
    document.querySelectorAll('a[href]').forEach(function(link){
      if(link.hasAttribute('download'))return;
      var raw=link.getAttribute('href');
      if(!raw||raw[0]==='#'||/^(?:mailto:|tel:|javascript:|data:)/i.test(raw))return;
      try{
        var u=new URL(raw,location.href);
        if(u.origin!==location.origin||!/^https?:$|^file:$/.test(u.protocol))return;
        if(!/(?:\.html?|\/$)/i.test(u.pathname))return;
        u.searchParams.set('theme',next);
        link.href=u.href;
      }catch(_){}
    });
  }
  root.setAttribute('data-theme',chosen());
  function mount(){
    var nav=document.querySelector('.site-header .nav');
    if(!nav)return;
    var lng=((root.getAttribute('lang')||'en').toLowerCase().split('-')[0]);
    var labels={
      en:{light:'Switch to light theme',dark:'Switch to dark theme'},
      uk:{light:'Увімкнути світлу тему',dark:'Увімкнути темну тему'},
      de:{light:'Helles Design einschalten',dark:'Dunkles Design einschalten'}
    }[lng]||{light:'Switch to light theme',dark:'Switch to dark theme'};
    var button=nav.querySelector('.theme-toggle');
    if(!button){
      button=document.createElement('button');
      button.className='theme-toggle';button.type='button';
      button.innerHTML='<svg class="theme-icon-light" aria-hidden="true" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg><svg class="theme-icon-dark" aria-hidden="true" viewBox="0 0 24 24"><path d="M20.9 13.3A9 9 0 0 1 10.7 3.1 9 9 0 1 0 20.9 13.3Z"/></svg>';
      var langPicker=nav.querySelector('.lang-switch');
      if(langPicker)nav.insertBefore(button,langPicker); else nav.appendChild(button);
    }
    function sync(){
      var light=root.getAttribute('data-theme')==='light';
      var label=light?labels.dark:labels.light;
      button.setAttribute('aria-label',label);
      button.setAttribute('title',label);
      button.setAttribute('aria-pressed',light?'true':'false');
    }
    button.addEventListener('click',function(){
      var next=root.getAttribute('data-theme')==='light'?'dark':'light';
      root.setAttribute('data-theme',next);
      store(next);
      transportLinks(next);
      sync();
    });
    transportLinks(root.getAttribute('data-theme'));
    sync();
    // BFCache back/forward restoration and preferences updated in another tab.
    window.addEventListener('pageshow',function(){
      var active=chosen();
      root.setAttribute('data-theme',active);
      transportLinks(active);
      sync();
    });
    window.addEventListener('storage',function(event){
      if(event.key!==KEY)return;
      var active=chosen();
      root.setAttribute('data-theme',active);
      transportLinks(active);
      sync();
    });
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount);
  else mount();
})();

(function(){
  'use strict';

  function ready(fn){
    if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  ready(function(){
    document.body.classList.add('scientific-system-v5','terminator-hud','research-storytelling');

    const toggle = document.querySelector('.nav-toggle');
    const links = document.querySelector('.nav-links');
    if (toggle && links) {
      toggle.addEventListener('click', function(){
        links.classList.toggle('open');
        toggle.setAttribute('aria-expanded', links.classList.contains('open') ? 'true' : 'false');
      });
    }

    const lang = ((document.documentElement.lang || 'en').toLowerCase().split('-')[0]);
    const dict = {
      en:{
        map:'Reading map', count:'sections', trace:'Research timeline',
        stages:['Definition','Adaptation','Reconfiguration','Survivability','Implementation'],
        mathTitle:'Mathematical orientation',
        mathContext:[
          'Irreversible damage separates the nominal plant from the degraded plant and changes the residual capability of available resources.',
          'Adaptation is bounded by the residual capability vector; preserving a task still requires a stability argument for the degraded dynamics.',
          'Reconfiguration first restricts the decision to feasible configurations and only then compares their mission-oriented value.',
          'Survivability requires structural admissibility and stability to hold together over time; an available route alone is not sufficient.',
          'Implementation must reproduce the same nominal/degraded distinction, residual-resource state and admissible supervisor decisions in executable form.'
        ],
        symbols:'Symbols', story:'Research story', question:'Question', evidence:'Evidence', next:'Next move',
        author:'Researcher', profiles:'Research profiles', current:'Current stage'
      },
      uk:{
        map:'Карта читання', count:'секцій', trace:'Таймлайн дослідження',
        stages:['Визначення','Адаптація','Реконфігурація','Живучість','Реалізація'],
        mathTitle:'Математична орієнтація',
        mathContext:[
          'Незворотне пошкодження відокремлює номінальний об’єкт від деградованого та змінює залишкову спроможність доступних ресурсів.',
          'Адаптація обмежена вектором залишкових спроможностей; збереження задачі все одно потребує аргументу стійкості для деградованої динаміки.',
          'Реконфігурація спочатку обмежує вибір допустимими конфігураціями і лише потім порівнює їхню цінність для місії.',
          'Живучість вимагає одночасної структурної допустимості та стійкості в часі; самого факту існування маршруту недостатньо.',
          'Реалізація має відтворювати ту саму відмінність між номінальною і деградованою моделями, стан залишкових ресурсів та допустимі рішення супервізора.'
        ],
        symbols:'Позначення', story:'Історія дослідження', question:'Питання', evidence:'Доказ / спостереження', next:'Наступний крок',
        author:'Дослідник', profiles:'Наукові профілі', current:'Поточний етап'
      },
      de:{
        map:'Lesekarte', count:'Abschnitte', trace:'Forschungszeitachse',
        stages:['Definition','Adaption','Rekonfiguration','Überlebensfähigkeit','Implementierung'],
        mathTitle:'Mathematische Orientierung',
        mathContext:[
          'Irreversibler Schaden trennt die nominale von der degradierten Anlage und verändert die verbleibende Fähigkeit verfügbarer Ressourcen.',
          'Adaption ist durch den Restfähigkeitsvektor begrenzt; der Erhalt einer Aufgabe benötigt weiterhin ein Stabilitätsargument für die degradierte Dynamik.',
          'Rekonfiguration beschränkt die Entscheidung zuerst auf zulässige Konfigurationen und vergleicht erst danach ihren Missionswert.',
          'Überlebensfähigkeit verlangt strukturelle Zulässigkeit und Stabilität gemeinsam über die Zeit; ein vorhandener Pfad allein genügt nicht.',
          'Die Implementierung muss dieselbe Trennung von nominalem und degradiertem Modell, den Restressourcenzustand und zulässige Supervisorentscheidungen ausführbar abbilden.'
        ],
        symbols:'Symbole', story:'Forschungsgeschichte', question:'Frage', evidence:'Evidenz / Beobachtung', next:'Nächster Schritt',
        author:'Forscher', profiles:'Forschungsprofile', current:'Aktuelle Phase'
      }
    };
    const tx = dict[lang] || dict.en;

    const main = document.querySelector('main');
    if (!main) return;

    const isUtility = document.body.classList.contains('redirect-page');
    if (isUtility) return;

    const siteScript = Array.from(document.scripts).find(function(s){ return /(?:^|\/)assets\/js\/site\.js(?:\?|$)/.test(s.src || ''); });
    const localeRoot = siteScript ? new URL('../../', siteScript.src) : new URL('./', document.baseURI);
    function siteHref(relative){ return new URL(relative, localeRoot).href; }

    const pathname = decodeURIComponent((location.pathname || '').toLowerCase());
    const relativePath = pathname.replace(/^.*?\/(uk\/|de\/)?/, function(m){ return m; });
    const hero = main.querySelector(':scope > section:first-child');
    // SCIENCE-01: scientific orientation belongs to the content owner, never the universal shell.
    // Only pages that explicitly opt in may receive research mathematics / timeline / story.
    const isHomepage = document.body.classList.contains('modular-home-page');
    const needsResearchPanels = !isHomepage && main.dataset.scientificPanels === 'true';

    function stageIndex(){
      if (pathname.indexOf('implementation') >= 0 || pathname.indexOf('/technology') >= 0) return 4;
      if (pathname.indexOf('exp-03-survivability') >= 0 || pathname.indexOf('survivability') >= 0) return 3;
      if (pathname.indexOf('exp-02-graph-reconfiguration') >= 0 || pathname.indexOf('reconfiguration') >= 0 || pathname.indexOf('/architecture') >= 0) return 2;
      if (pathname.indexOf('evolution') >= 0 || pathname.indexOf('exp-01-irreversible') >= 0 || pathname.indexOf('adaptation') >= 0) return 1;
      return 0;
    }
    const currentStage = stageIndex();

    // Public-content hygiene for frozen course HTML: presentation rules belong in code/rulebook, not reader-facing copy.
    if (/\/teaching\/embedded-software-engineering\/index\.html$/.test(pathname)) {
      const courseMapCopy = document.querySelector('.course-map-head p');
      if (courseMapCopy) {
        courseMapCopy.textContent = {
          en:'Dated modules trace the course from embedded-system foundations through delivery, commercial engineering, requirements and architecture.',
          uk:'Датовані модулі простежують розвиток курсу від основ embedded-систем через delivery і commercial engineering до вимог та архітектури.',
          de:'Datierte Module verfolgen den Kurs von Embedded-Grundlagen über Delivery und Commercial Engineering bis zu Anforderungen und Architektur.'
        }[lang] || '';
      }
    }

    const mathModels = [
      {
        tex:[
          String.raw`\mathcal P_0 \xrightarrow{\mathcal D} \mathcal P_d`,
          String.raw`\boldsymbol{\rho}(t)\in[0,1]^n`
        ],
        fallback:['P₀  ─D→  Pᵈ','ρ(t) ∈ [0,1]ⁿ'],
        defs:{
          en:[['P₀','nominal plant/model before irreversible damage'],['D','damage event or degradation operator'],['Pᵈ','degraded plant/model after damage'],['ρᵢ(t)','normalized residual capability of resource i; 0 = unavailable, 1 = nominal']],
          uk:[['P₀','номінальний об’єкт / модель до незворотного пошкодження'],['D','подія пошкодження або оператор деградації'],['Pᵈ','деградований об’єкт / модель після пошкодження'],['ρᵢ(t)','нормована залишкова спроможність ресурсу i; 0 = недоступний, 1 = номінальний']],
          de:[['P₀','nominale Anlage / Modell vor irreversibler Schädigung'],['D','Schadensereignis bzw. Degradationsoperator'],['Pᵈ','degradierte Anlage / Modell nach dem Schaden'],['ρᵢ(t)','normierte Restfähigkeit der Ressource i; 0 = nicht verfügbar, 1 = nominal']]
        }
      },
      {
        tex:[
          String.raw`\boldsymbol{\rho}(t)\in[0,1]^n`,
          String.raw`V(\mathbf x)=\mathbf x^\top P\mathbf x,\qquad P\succ0`
        ],
        fallback:['ρ(t) ∈ [0,1]ⁿ','V(x) = xᵀPx,   P ≻ 0'],
        defs:{
          en:[['ρ(t)','vector of residual resource capabilities'],['x','state vector of the controlled system'],['P','positive-definite matrix defining the Lyapunov function'],['V(x)','candidate stability measure used to reason about admissible degraded operation']],
          uk:[['ρ(t)','вектор залишкових спроможностей ресурсів'],['x','вектор стану керованої системи'],['P','додатно визначена матриця функції Ляпунова'],['V(x)','кандидатна міра стійкості для аналізу допустимого деградованого режиму']],
          de:[['ρ(t)','Vektor der verbleibenden Ressourcenfähigkeiten'],['x','Zustandsvektor des geregelten Systems'],['P','positiv definite Matrix der Lyapunov-Funktion'],['V(x)','Kandidatenmaß für Stabilität im zulässigen degradierten Betrieb']]
        }
      },
      {
        tex:[
          String.raw`S(c,\boldsymbol{\rho})=\sum_{j=1}^{m} w_j f_j(\boldsymbol{\rho})\,\delta_j(c)`,
          String.raw`c^\star\in\operatorname*{arg\,max}_{c\in\mathcal C_{\mathrm{feas}}(\boldsymbol{\rho})} S(c,\boldsymbol{\rho})`
        ],
        fallback:['S(c,ρ) = Σⱼ wⱼ fⱼ(ρ) δⱼ(c)','c* ∈ arg max  S(c,ρ),   c ∈ Cfeas(ρ)'],
        defs:{
          en:[['c','candidate system configuration'],['Cfeas(ρ)','configurations feasible for the current residual resources'],['fⱼ(ρ)','realizable quality/capability of function j under ρ'],['δⱼ(c)','configuration-dependent activation/assignment term for function j'],['wⱼ','mission weight of function j'],['S(c,ρ)','configuration score used only among feasible candidates']],
          uk:[['c','кандидатна конфігурація системи'],['Cfeas(ρ)','конфігурації, допустимі за поточного вектора залишкових ресурсів'],['fⱼ(ρ)','реалізовна якість / спроможність функції j за ρ'],['δⱼ(c)','залежний від конфігурації терм активації / призначення функції j'],['wⱼ','вага функції j для місії'],['S(c,ρ)','оцінка конфігурації, що порівнюється лише серед допустимих кандидатів']],
          de:[['c','Kandidatenkonfiguration des Systems'],['Cfeas(ρ)','für die aktuellen Restressourcen zulässige Konfigurationen'],['fⱼ(ρ)','realisierbare Qualität/Fähigkeit der Funktion j unter ρ'],['δⱼ(c)','konfigurationsabhängiger Aktivierungs-/Zuordnungsterm der Funktion j'],['wⱼ','Missionsgewicht der Funktion j'],['S(c,ρ)','Konfigurationsbewertung nur innerhalb der zulässigen Kandidaten']]
        }
      },
      {
        tex:[
          String.raw`c^\star\in\operatorname*{arg\,max}_{c\in\mathcal C_{\mathrm{feas}}(\boldsymbol{\rho})} S(c,\boldsymbol{\rho})`,
          String.raw`V(\mathbf x)=\mathbf x^\top P\mathbf x,\qquad P\succ0`
        ],
        fallback:['c* ∈ arg max  S(c,ρ),   c ∈ Cfeas(ρ)','V(x) = xᵀPx,   P ≻ 0'],
        defs:{
          en:[['Cfeas(ρ)','set of degraded configurations that satisfy the active feasibility constraints'],['c*','selected admissible configuration'],['S(c,ρ)','mission-oriented score of an admissible configuration'],['V(x)','stability certificate used alongside structural feasibility; selection alone does not prove stability']],
          uk:[['Cfeas(ρ)','множина деградованих конфігурацій, що задовольняють активні обмеження допустимості'],['c*','обрана допустима конфігурація'],['S(c,ρ)','орієнтована на місію оцінка допустимої конфігурації'],['V(x)','сертифікат стійкості, що розглядається разом зі структурною допустимістю; сам вибір конфігурації не доводить стійкість']],
          de:[['Cfeas(ρ)','Menge degradierter Konfigurationen, die die aktiven Zulässigkeitsbedingungen erfüllen'],['c*','gewählte zulässige Konfiguration'],['S(c,ρ)','missionsorientierte Bewertung einer zulässigen Konfiguration'],['V(x)','Stabilitätszertifikat zusätzlich zur strukturellen Zulässigkeit; Auswahl allein beweist keine Stabilität']]
        }
      },
      {
        tex:[
          String.raw`\mathcal P_0 \xrightarrow{\mathcal D} \mathcal P_d`,
          String.raw`c^\star\in\operatorname*{arg\,max}_{c\in\mathcal C_{\mathrm{feas}}(\boldsymbol{\rho})} S(c,\boldsymbol{\rho})`
        ],
        fallback:['P₀  ─D→  Pᵈ','c* ∈ arg max  S(c,ρ),   c ∈ Cfeas(ρ)'],
        defs:{
          en:[['P₀ → Pᵈ','implementation must preserve the distinction between nominal and post-damage models'],['ρ','runtime estimate of residual resource capability'],['Cfeas(ρ)','runtime-feasible configuration set'],['c*','configuration selected by the supervisor from feasible successors']],
          uk:[['P₀ → Pᵈ','реалізація повинна зберігати відмінність між номінальною та післяаварійною моделями'],['ρ','runtime-оцінка залишкової спроможності ресурсів'],['Cfeas(ρ)','множина конфігурацій, допустимих у поточному runtime-стані'],['c*','конфігурація, обрана супервізором серед допустимих наступників']],
          de:[['P₀ → Pᵈ','die Implementierung muss zwischen nominalem und nachschadigem Modell unterscheiden'],['ρ','Laufzeitschätzung der verbleibenden Ressourcenfähigkeit'],['Cfeas(ρ)','zur Laufzeit zulässige Konfigurationsmenge'],['c*','vom Supervisor aus zulässigen Nachfolgern gewählte Konfiguration']]
        }
      }
    ];

    function ensureMathJax(layer){
      function activate(){
        if (!window.MathJax || typeof window.MathJax.typesetPromise !== 'function') return;
        layer.classList.add('mathjax-ready');
        window.MathJax.typesetPromise([layer]).catch(function(){ layer.classList.remove('mathjax-ready'); });
      }
      if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') { activate(); return; }
      window.MathJax = window.MathJax || {};
      window.MathJax.tex = window.MathJax.tex || {inlineMath:[['\\(','\\)']],displayMath:[['\\[','\\]']]};
      window.MathJax.svg = window.MathJax.svg || {fontCache:'global'};
      const existing = Array.from(document.scripts).find(function(s){ return /mathjax@3|tex-svg\.js|tex-mml-chtml\.js/.test(s.src || ''); });
      if (existing) {
        existing.addEventListener('load', function(){ setTimeout(activate, 0); }, {once:true});
        setTimeout(activate, 600);
        return;
      }
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
      script.defer = true;
      script.dataset.vaeringjarMathjax = 'true';
      script.addEventListener('load', function(){ setTimeout(activate, 0); });
      document.head.appendChild(script);
    }

    if (hero && needsResearchPanels && !document.querySelector('.scientific-math-layer')) {
      const model = mathModels[currentStage] || mathModels[0];
      const defs = model.defs[lang] || model.defs.en;
      const math = document.createElement('section');
      math.className = 'scientific-math-layer';
      math.setAttribute('aria-label', tx.mathTitle);
      const formulas = model.tex.map(function(tex, idx){
        return '<div class="scientific-math-formula"><span class="math-fallback">'+model.fallback[idx]+'</span><span class="math-tex">\\['+tex+'\\]</span></div>';
      }).join('');
      const legend = defs.map(function(pair){
        return '<div class="math-symbol"><b>'+pair[0]+'</b><span>'+pair[1]+'</span></div>';
      }).join('');
      math.innerHTML =
        '<div class="container"><div class="scientific-math-panel">' +
          '<div class="scientific-math-head"><div><strong>'+tx.mathTitle+'</strong><p>'+tx.mathContext[currentStage]+'</p></div><span class="math-stage">0'+(currentStage+1)+' · '+tx.stages[currentStage]+'</span></div>' +
          '<div class="scientific-math-formulas">'+formulas+'</div>' +
          '<details class="scientific-math-legend" open><summary>'+tx.symbols+'</summary><div class="math-symbol-grid">'+legend+'</div></details>' +
        '</div></div>';
      hero.insertAdjacentElement('afterend', math);
      ensureMathJax(math);
    }

    if (hero && needsResearchPanels && !document.querySelector('.research-method-trace')) {
      const stageTargets = [
        'programme.html',
        'evolution.html',
        'research/experiments/exp-02-graph-reconfiguration/index.html',
        'research/experiments/exp-03-survivability-driven-reconfiguration/index.html',
        'implementation.html'
      ];
      const trace = document.createElement('section');
      trace.className = 'research-method-trace';
      trace.setAttribute('aria-label', tx.trace);
      const wrap = document.createElement('div'); wrap.className = 'container';
      const label = document.createElement('div'); label.className = 'trace-label'; label.textContent = tx.trace;
      const grid = document.createElement('div'); grid.className = 'trace-grid';
      tx.stages.forEach(function(step, idx){
        const a = document.createElement('a');
        a.className = 'trace-step' + (idx === currentStage ? ' is-current' : '');
        a.href = siteHref(stageTargets[idx]);
        a.setAttribute('data-stage', String(idx + 1));
        a.title = step;
        if (idx === currentStage) a.setAttribute('aria-current','step');
        const small = document.createElement('small'); small.textContent = String(idx+1).padStart(2,'0');
        const b = document.createElement('b'); b.textContent = step;
        a.appendChild(small); a.appendChild(b);
        if(idx === currentStage){ const em=document.createElement('em'); em.textContent=tx.current; a.appendChild(em); }
        grid.appendChild(a);
      });
      wrap.appendChild(label); wrap.appendChild(grid); trace.appendChild(wrap);
      const mathLayer = document.querySelector('.scientific-math-layer');
      if (mathLayer) mathLayer.insertAdjacentElement('afterend', trace);
      else hero.insertAdjacentElement('afterend', trace);
    }

    const storyData = {
      en:[
        ['What remains of the system after an irreversible failure?','Represent the transition from the nominal plant to the degraded plant and make residual resource capability explicit.','Test whether adaptation can preserve the mission without changing structure.'],
        ['Can parameter adaptation alone absorb irreversible resource loss?','A degraded resource vector can preserve part of the mission, but structural limits remain when a required resource disappears.','Permit a controlled change of system configuration.'],
        ['Which surviving structure should the supervisor choose?','Only configurations in Cfeas(ρ) are candidates; the score S(c,ρ) orders admissible alternatives rather than legitimising infeasible ones.','Ask whether the selected degraded mission remains stable and survivable over time.'],
        ['When is continued degraded operation scientifically defensible?','Structural feasibility must be considered together with residual mission value and a stability argument; “a route exists” is not enough.','Transfer the model into executable supervisory logic and validate it under injected faults.'],
        ['Can the research model survive contact with implementation?','Runtime resource estimates, feasible-successor logic and supervisor decisions must be reproducible in software/hardware experiments.','Feed implementation evidence back into the model and revise assumptions when evidence contradicts them.']
      ],
      uk:[
        ['Що залишається від системи після незворотної відмови?','Перехід від номінального об’єкта до деградованого потрібно описати формально, а залишкові спроможності ресурсів зробити явними.','Перевірити, чи достатньо адаптації без зміни структури для збереження місії.'],
        ['Чи здатна лише параметрична адаптація компенсувати незворотну втрату ресурсу?','Вектор залишкових ресурсів може зберегти частину функцій, але зникнення критичного ресурсу створює структурне обмеження.','Дозволити керовану зміну конфігурації системи.'],
        ['Яку зі структур, що залишилися, повинен обрати супервізор?','Кандидатами є лише конфігурації з Cfeas(ρ); S(c,ρ) ранжує допустимі альтернативи, але не робить недопустиму конфігурацію допустимою.','Перевірити, чи залишається обрана деградована місія стійкою та живучою в часі.'],
        ['Коли продовження деградованої роботи можна вважати обґрунтованим?','Структурну допустимість потрібно розглядати разом із залишковою цінністю місії та аргументом стійкості; самого факту існування маршруту недостатньо.','Перенести модель у виконувану супервізорну логіку та валідувати її ін’єкцією відмов.'],
        ['Чи витримує дослідницька модель контакт із реальною реалізацією?','Runtime-оцінка ресурсів, логіка допустимих переходів і рішення супервізора мають відтворюватися у програмно-апаратному експерименті.','Повернути експериментальні докази назад у модель і змінювати припущення, якщо дані їм суперечать.']
      ],
      de:[
        ['Was bleibt vom System nach einem irreversiblen Ausfall?','Der Übergang von der nominalen zur degradierten Anlage und die verbleibenden Ressourcenfähigkeiten müssen formal sichtbar werden.','Prüfen, ob reine Adaption die Mission ohne Strukturänderung erhält.'],
        ['Kann Parameteradaption allein irreversiblen Ressourcenverlust auffangen?','Ein degradierter Ressourcenvektor kann Funktionen teilweise erhalten, doch der Verlust einer notwendigen Ressource erzeugt strukturelle Grenzen.','Eine kontrollierte Rekonfiguration der Systemstruktur zulassen.'],
        ['Welche überlebende Struktur soll der Supervisor wählen?','Nur Konfigurationen in Cfeas(ρ) sind Kandidaten; S(c,ρ) ordnet zulässige Alternativen, legitimiert aber keine unzulässigen.','Prüfen, ob die gewählte degradierte Mission stabil und überlebensfähig bleibt.'],
        ['Wann ist fortgesetzter degradierter Betrieb wissenschaftlich vertretbar?','Strukturelle Zulässigkeit muss zusammen mit Restmissionswert und Stabilitätsargument betrachtet werden; ein vorhandener Pfad allein genügt nicht.','Das Modell in ausführbare Supervisorlogik überführen und unter injizierten Fehlern validieren.'],
        ['Hält das Forschungsmodell der Implementierung stand?','Laufzeit-Ressourcenschätzung, zulässige Nachfolger und Supervisorentscheidungen müssen in Software-/Hardwareexperimenten reproduzierbar sein.','Implementierungsevidenz in das Modell zurückführen und Annahmen bei Widerspruch revidieren.']
      ]
    };

    if (hero && needsResearchPanels && !document.querySelector('.research-story-bridge')) {
      const story = (storyData[lang] || storyData.en)[currentStage];
      const sec = document.createElement('section');
      sec.className = 'research-story-bridge';
      sec.setAttribute('aria-label', tx.story);
      sec.innerHTML = '<div class="container"><div class="story-head"><span>'+tx.story+'</span><b>0'+(currentStage+1)+' / 05 · '+tx.stages[currentStage]+'</b></div><div class="story-grid">' +
        '<article><small>'+tx.question+'</small><p>'+story[0]+'</p></article>' +
        '<article><small>'+tx.evidence+'</small><p>'+story[1]+'</p></article>' +
        '<article><small>'+tx.next+'</small><p>'+story[2]+'</p></article>' +
      '</div></div>';
      const trace = document.querySelector('.research-method-trace');
      if(trace) trace.insertAdjacentElement('afterend', sec);
    }

    const hasDedicatedReaderNav = document.querySelector('.module-local-nav, .lecture-article, .course-map-v3');
    if (needsResearchPanels && !hasDedicatedReaderNav && !document.querySelector('.scientific-section-map')) {
      const directSections = Array.from(main.children).filter(function(el){
        return el.tagName === 'SECTION' &&
          !el.classList.contains('module-nextprev') &&
          !el.classList.contains('scientific-section-map') &&
          !el.classList.contains('research-method-trace') &&
          !el.classList.contains('research-story-bridge') &&
          !el.classList.contains('scientific-math-layer');
      });
      const candidates = directSections.filter(function(sec, index){
        if(index === 0 && sec.querySelector('h1')) return false;
        return !!sec.querySelector('h2, h3');
      });
      if(candidates.length >= 3){
        const visible = candidates.slice(0, 6);
        visible.forEach(function(sec, idx){ if(!sec.id) sec.id = 'section-' + String(idx+1).padStart(2,'0'); });
        const map = document.createElement('section');
        map.className = 'scientific-section-map';
        map.setAttribute('aria-label', tx.map);
        const container = document.createElement('div'); container.className = 'container';
        const head = document.createElement('div'); head.className = 'scientific-map-head';
        head.innerHTML = '<strong>'+tx.map+'</strong><span>'+visible.length+(candidates.length>visible.length?' / '+candidates.length:'')+' '+tx.count+'</span>';
        const grid = document.createElement('div'); grid.className = 'scientific-map-grid';
        visible.forEach(function(sec, idx){
          const heading = sec.querySelector('h2, h3');
          const title = heading ? heading.textContent.trim().replace(/\s+/g,' ') : ('Section '+(idx+1));
          const a = document.createElement('a');
          a.className = 'scientific-map-link';
          a.href = '#'+sec.id;
          a.innerHTML = '<small>'+String(idx+1).padStart(2,'0')+'</small><b></b>';
          a.querySelector('b').textContent = title;
          grid.appendChild(a);
        });
        container.appendChild(head); container.appendChild(grid); map.appendChild(container);
        const story = document.querySelector('.research-story-bridge');
        if (story) story.insertAdjacentElement('afterend', map);
        else if(hero) hero.insertAdjacentElement('afterend', map);
      }
    }

    function isIdentityPage(){
      const clean = pathname.replace(/\/+$/,'');
      return /\/(about|index)\.html$/.test(clean) || clean === '' || clean === '/' || /\/(uk|de)$/.test(clean);
    }
    if (isIdentityPage() && !isHomepage && !document.querySelector('.researcher-identity')) {
      const identity = document.createElement('section');
      identity.className = 'researcher-identity';
      identity.setAttribute('aria-label', tx.profiles);
      const copy = {
        en:'Dmytro Humennyi, Ph.D. · Associate Professor · embedded systems, robotics, post-failure control and survivability-oriented reconfiguration.',
        uk:'Дмитро Гуменний, Ph.D. · доцент · вбудовані системи, робототехніка, післяаварійне керування та реконфігурація, орієнтована на живучість.',
        de:'Dmytro Humennyi, Ph.D. · Associate Professor · Embedded Systems, Robotik, Post-Failure Control und überlebensorientierte Rekonfiguration.'
      }[lang] || '';
      identity.innerHTML = '<div class="container"><div class="researcher-card"><div class="researcher-copy"><span>'+tx.author+'</span><h2>Dmytro Humennyi · Дмитро Гуменний</h2><p>'+copy+'</p></div><nav class="researcher-links" aria-label="'+tx.profiles+'">' +
        '<a href="https://orcid.org/0000-0001-6736-0543" target="_blank" rel="me noopener">ORCID</a>' +
        '<a href="https://fait.knuba.edu.ua/kafedra-kbki/sklad-kafedri/gumennij-dmitro-oleksandrovich/" target="_blank" rel="noopener">KNUCA</a>' +
        '<a href="https://intellect.kpi.ua/uk/profile/gdo40" target="_blank" rel="noopener">KPI Intellect</a>' +
        '<a href="http://tc.kpi.ua/uk/staff-3" target="_blank" rel="noopener">KPI TC archive</a>' +
        '<a href="https://www.researchgate.net/profile/Dmytro-Humennyi?ev=hdr_xprf" target="_blank" rel="noopener">ResearchGate</a>' +
      '</nav></div></div>';
      main.appendChild(identity);
    }
  });
})();
