(() => {
  const page = document.querySelector('[data-exp02]');
  if (!page) return;
  const dataUrl = page.dataset.scenario;
  let data;
  let mode = 'nominal';
  let selectedPath = [];
  let bestTarget = null;
  let shortest = {};
  let animationTimer = null;

  const $ = (s, ctx=document) => ctx.querySelector(s);
  const $$ = (s, ctx=document) => [...ctx.querySelectorAll(s)];

  const fmt = (v, d=2) => Number(v).toFixed(d);
  const edgeAvailable = (e, m) => e.modes.includes(m);
  const stateById = id => data.states.find(s => s.id === id);
  const feasible = (id,m) => !!stateById(id)?.feasible?.[m];

  function dijkstra(start, graphMode='damaged') {
    const ids=data.states.filter(s=>s.feasible[graphMode]).map(s=>s.id);
    const dist=Object.fromEntries(ids.map(id=>[id,Infinity]));
    const prev={}; dist[start]=0;
    const q=new Set(ids);
    while(q.size){
      let u=null, best=Infinity;
      for(const id of q){ if(dist[id]<best){best=dist[id];u=id;} }
      if(u===null) break; q.delete(u);
      for(const e of data.edges.filter(e=>e.from===u && edgeAvailable(e,graphMode) && feasible(e.to,graphMode))){
        const alt=dist[u]+e.cost;
        if(alt<dist[e.to]){dist[e.to]=alt;prev[e.to]=u;}
      }
    }
    const pathTo=id=>{
      if(!Number.isFinite(dist[id])) return [];
      const p=[id]; let cur=id;
      while(cur!==start){cur=prev[cur];if(!cur)return [];p.unshift(cur)}
      return p;
    };
    return {dist,prev,pathTo};
  }

  function computeTarget(){
    const start=data.post_damage.capture;
    shortest=dijkstra(start,'damaged');
    const lambda=data.model.lambda;
    let best={id:start,score:-Infinity,path:[start],cost:0};
    for(const s of data.states){
      if(!s.feasible.damaged || s.id===start) continue;
      const cost=shortest.dist[s.id]; if(!Number.isFinite(cost)) continue;
      const score=s.utility-lambda*cost;
      if(score>best.score) best={id:s.id,score,path:shortest.pathTo(s.id),cost};
    }
    bestTarget=best; selectedPath=best.path;
  }

  function renderResources(){
    const vals=mode==='nominal'?data.resources.nominal:data.resources.damaged;
    const root=$('[data-resources]');
    root.innerHTML=data.resources.labels.map((l,i)=>`<div class="exp02-resource ${vals[i]===0?'lost':''}"><small>${l}</small><b>${fmt(vals[i])}</b></div>`).join('');
    $('[data-resource-caption]').textContent=mode==='nominal'?'ρ₀ — nominal residual-resource vector':`ρd — ${data.resources.event}`;
  }

  function renderMatrix(kind){
    const target=$(`[data-matrix="${kind}"]`); if(!target) return;
    const ids=data.states.map(s=>s.id);
    const matrixMode=mode==='nominal'?'nominal':'damaged';
    let html='<table class="exp02-matrix"><thead><tr><th></th>'+ids.map(id=>`<th>${id}</th>`).join('')+'</tr></thead><tbody>';
    for(const r of ids){
      html+=`<tr><th class="row-head">${r}</th>`;
      for(const c of ids){
        if(!feasible(r,matrixMode)||!feasible(c,matrixMode)){html+='<td class="matrix-na">×</td>';continue;}
        const e=data.edges.find(e=>e.from===r&&e.to===c&&edgeAvailable(e,matrixMode));
        if(kind==='adj') html+=e?'<td class="matrix-one">1</td>':'<td class="matrix-zero">0</td>';
        else {
          if(r===c){html+='<td class="matrix-zero">0</td>';continue;}
          if(!e){html+='<td class="matrix-zero">∞</td>';continue;}
          const cls=e.cost<.10?'low':e.cost<.16?'mid':'high';
          html+=`<td class="matrix-cost ${cls}">${fmt(e.cost)}</td>`;
        }
      }
      html+='</tr>';
    }
    html+='</tbody></table>'; target.innerHTML=html;
  }

  function renderScoreTable(){
    const body=$('[data-score-body]');
    const lambda=data.model.lambda;
    body.innerHTML=data.states.map(s=>{
      const f=s.feasible.damaged;
      const c=f && Number.isFinite(shortest.dist[s.id])?shortest.dist[s.id]:null;
      const score=c===null?null:s.utility-lambda*c;
      return `<tr class="${!f?'infeasible':''} ${s.id===bestTarget.id?'selected':''}"><td>${s.id} · ${s.short}</td><td>${f?'yes':'no'}</td><td class="num">${fmt(s.utility)}</td><td class="num">${c===null?'—':fmt(c)}</td><td class="num">${score===null?'—':fmt(score)}</td></tr>`;
    }).join('');
    $('[data-target]').textContent=bestTarget.id;
    $('[data-target-score]').textContent=fmt(bestTarget.score);
  }

  function edgePath(a,b){
    const dx=b.x-a.x, dy=b.y-a.y; const len=Math.hypot(dx,dy)||1;
    const padA=50,padB=56;
    const x1=a.x+dx/len*padA, y1=a.y+dy/len*padA;
    const x2=b.x-dx/len*padB, y2=b.y-dy/len*padB;
    return `M ${x1} ${y1} L ${x2} ${y2}`;
  }

  function renderGraph(pathStep=-1){
    const svg=$('[data-state-graph]');
    const effective=mode==='nominal'?'nominal':'damaged';
    const pathPairs=new Set(selectedPath.slice(0,-1).map((x,i)=>`${x}>${selectedPath[i+1]}`));
    let parts=[`<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 z" fill="rgba(126,170,132,.6)"/></marker><marker id="arrow-red" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 z" fill="#ff4b3e"/></marker></defs>`];
    for(const e of data.edges){
      const a=stateById(e.from),b=stateById(e.to); if(!a||!b)continue;
      const avail=edgeAvailable(e,effective)&&feasible(e.from,effective)&&feasible(e.to,effective);
      if(mode==='nominal'&&!edgeAvailable(e,'nominal')) continue;
      let cls='graph-edge';
      if(!avail)cls+=' disabled';
      if(mode==='path'&&pathPairs.has(`${e.from}>${e.to}`)){
        const idx=selectedPath.indexOf(e.from);
        if(pathStep<0||idx<pathStep) cls+=' selected';
      }
      parts.push(`<path class="${cls}" d="${edgePath(a,b)}"><title>${e.from} → ${e.to}; C=${fmt(e.cost)}; T=${fmt(e.duration_s)} s</title></path>`);
    }
    if(mode!=='nominal'){
      const v0=stateById('V0'),v1=stateById(data.post_damage.capture), q={x:150,y:225};
      parts.push(`<path class="graph-event-edge" d="M ${v0.x} ${v0.y+38} L ${q.x} ${q.y-23}"/>`);
      parts.push(`<path class="graph-event-edge" d="M ${q.x} ${q.y+23} L ${v1.x} ${v1.y-44}"/>`);
      parts.push(`<g class="graph-transient" transform="translate(${q.x},${q.y})"><polygon points="0,-24 42,0 0,24 -42,0"/><text text-anchor="middle" y="4">q_f</text></g>`);
    }
    for(const s of data.states){
      const isF=s.feasible[effective];
      let cls='graph-node'; if(!isF)cls+=' disabled';
      if(mode==='path'&&s.id===selectedPath[Math.max(0,Math.min(pathStep,selectedPath.length-1))]) cls+=' current';
      else if(mode!=='nominal'&&s.id===data.post_damage.capture) cls+=' current';
      if(mode!=='nominal'&&s.id===bestTarget.id) cls+=' target';
      if(mode==='path'&&pathStep>=0){const idx=selectedPath.indexOf(s.id);if(idx>=0&&idx>pathStep) cls+=' disabled';}
      parts.push(`<g class="${cls}" transform="translate(${s.x},${s.y})"><rect x="-58" y="-38" width="116" height="76"/><text class="node-id" text-anchor="middle" y="-13">${s.id}</text><text class="node-label" text-anchor="middle" y="4">${s.short.toUpperCase()}</text><text class="node-value" text-anchor="middle" y="22">Φ=${fmt(s.utility)}</text><title>${s.id} — ${s.label}: ${s.note}</title></g>`);
    }
    svg.innerHTML=parts.join('');
  }

  function renderTrace(active=-1){
    const steps=[
      {small:'EVENT',b:'Irreversible loss',span:data.resources.event},
      {small:'CAPTURE',b:'q_f → V1',span:'enter certified stable capture basin'},
      {small:'TRANSITION 01',b:'V1 → V2',span:'reallocate actuation; reduce bandwidth'},
      {small:'TRANSITION 02',b:'V2 → V4',span:'prioritise mission-essential functions'},
      {small:'SETTLE',b:'V4 stable',span:'verify Φ and safety envelope'},
    ];
    $('[data-trace]').innerHTML=steps.map((s,i)=>`<div class="trace-step ${i<=active?'active':''}"><small>${s.small}</small><b>${s.b}</b><span>${s.span}</span></div>`).join('');
  }

  function renderPathMetrics(){
    const edges=[]; for(let i=0;i<selectedPath.length-1;i++) edges.push(data.edges.find(e=>e.from===selectedPath[i]&&e.to===selectedPath[i+1]&&edgeAvailable(e,'damaged')));
    const time=edges.reduce((a,e)=>a+e.duration_s,0);
    const risk=edges.reduce((a,e)=>a+e.components.risk,0);
    $('[data-path]').textContent=`q_f → ${selectedPath.join(' → ')}`;
    $('[data-path-cost]').textContent=fmt(bestTarget.cost);
    $('[data-path-time]').textContent=`${fmt(time)} s`;
    $('[data-path-risk]').textContent=fmt(risk);
    $('[data-path-utility]').textContent=fmt(stateById(bestTarget.id).utility);
  }

  function setMode(next){
    clearInterval(animationTimer); mode=next;
    $$('[data-mode]').forEach(b=>b.classList.toggle('active',b.dataset.mode===mode));
    $('[data-matrix-mode]').textContent=mode==='nominal'?'NOMINAL ρ₀':'POST-DAMAGE ρd';
    renderResources();renderMatrix('adj');renderMatrix('cost');renderGraph();renderTrace(mode==='nominal'?-1:1);
  }

  function animate(){
    clearInterval(animationTimer); mode='path';
    $$('[data-mode]').forEach(b=>b.classList.toggle('active',b.dataset.mode==='path'));
    renderResources();renderMatrix('adj');renderMatrix('cost');
    let step=0; renderTrace(0); renderGraph(0);
    animationTimer=setInterval(()=>{
      step++;
      renderTrace(Math.min(step+1,4));
      renderGraph(Math.min(step,selectedPath.length-1));
      if(step>=selectedPath.length){clearInterval(animationTimer);}
    },850);
  }

  function init(d){
    data=d;computeTarget();renderScoreTable();renderPathMetrics();setMode('nominal');
    $$('[data-mode]').forEach(b=>b.addEventListener('click',()=>setMode(b.dataset.mode)));
    $('[data-run]').addEventListener('click',animate);
  }
  try {
    const embedded=$('#exp02-scenario');
    if(embedded) init(JSON.parse(embedded.textContent));
    else fetch(dataUrl).then(r=>{if(!r.ok)throw new Error(r.status);return r.json()}).then(init).catch(err=>{
      console.error(err); const msg=$('[data-load-error]'); if(msg) msg.hidden=false;
    });
  } catch(err) {
    console.error(err); const msg=$('[data-load-error]'); if(msg) msg.hidden=false;
  }
})();
