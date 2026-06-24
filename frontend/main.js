'use strict';
// main.js — Ansichtswechsel, Login, Live-Refresh, Verdrahtung, Rechtsseiten, Init. Zuletzt laden.

// ---- View switching -------------------------------------------------------
function switchView(v){
  state.view=v;
  $$('.tab').forEach(t=>t.classList.toggle('active',t.dataset.view===v));
  $('#view-list').classList.toggle('hidden',v!=='list');
  $('#view-stats').classList.toggle('hidden',v!=='stats');
  $('#exportStatsPdf').classList.toggle('hidden',v!=='stats');
  $('#exportTablePdf').classList.toggle('hidden',v!=='list');
  if(v==='stats') loadStatsView();
}

// ---- Login ----------------------------------------------------------------
function refreshLoginBtn(){
  $('#loginBtn').textContent = state.pw?'🔓 Team (angemeldet)':'🔒 Team-Login';
  // Team-only Filter (Prüfung/Herkunft) nur nach Login zeigen; beim Abmelden zurücksetzen.
  $$('.team-only').forEach(e=>e.classList.toggle('hidden', !state.pw));
  if(!state.pw && $('#f-pruef')) $('#f-pruef').value='';
}
async function doLogin(){
  const pw=$('#pwInput').value;
  try{ const r=await fetch('/api/auth',{method:'POST',headers:{'X-Team-Password':pw}}); if(!r.ok)throw 0;
    state.pw=pw; sessionStorage.setItem('qe_pw',pw); $('#loginOverlay').classList.add('hidden'); $('#pwErr').classList.add('hidden'); refreshLoginBtn();
    if(state.view==='stats') loadStatsView();
    toast('Team-Login aktiv — interne Infos sichtbar.');
  }catch{ $('#pwErr').classList.remove('hidden'); }
}

// ---- Datenstand & Live-Refresh --------------------------------------------
async function loadFreshness(){
  try{ const s=await api('/api/stats'); const ts=s.meta?.generatedAt;
    state.dataStand = ts || '';
    $('#freshness').textContent = ts?`Datenstand: ${ts}`:''; }catch{}
}
let polling=false;
async function startRefresh(){
  if(polling) return;
  try{
    const r=await fetch('/jobs/refresh',{method:'POST',headers:headers()});
    if(!r.ok){ toast('Refresh konnte nicht gestartet werden.'); return; }
    polling=true; $('#refreshBtn').disabled=true;
    toast('Live-Aktualisierung gestartet …');
    pollRefresh();
  }catch{ toast('Refresh konnte nicht gestartet werden.'); }
}
async function pollRefresh(){
  try{
    const j=await api('/jobs/latest');
    if(j.status==='running'){ $('#refreshBtn').textContent=`⏳ ${j.percent||0}%`; $('#freshness').textContent=j.message||''; setTimeout(pollRefresh,1500); return; }
    polling=false; $('#refreshBtn').disabled=false; $('#refreshBtn').textContent='🔄 Aktualisieren';
    if(j.status==='done'){ toast(`Live-Daten aktualisiert (${(j.meta?.total||0).toLocaleString('de')} Quellen).`); state.page=1; loadList(); loadFreshness(); if(state.view==='stats') loadStatsView(); }
    else if(j.status==='error'){ toast('Refresh-Fehler: '+(j.error||'unbekannt')); loadFreshness(); }
  }catch{ polling=false; $('#refreshBtn').disabled=false; $('#refreshBtn').textContent='🔄 Aktualisieren'; }
}

// ---- Wire up --------------------------------------------------------------
function resetFilters(){ ['f-pruef','f-subject','f-level','f-lrt','f-license','f-language'].forEach(i=>$('#'+i).value='');
  $('#f-art').value='';   // Default = alle Quellen
  $('#f-sort').value='contentCount|desc'; $('#f-mincount').value=0;$('#mc-val').textContent='0';
  ['f-oer','f-fp'].forEach(i=>$('#'+i).checked=false); $('#search').value=''; state.page=1; loadList(); }
let deb; const reload=()=>{ state.page=1; clearTimeout(deb); deb=setTimeout(loadList,180); };
['#f-art','#f-pruef','#f-subject','#f-level','#f-lrt','#f-license','#f-language','#f-sort','#f-oer','#f-fp'].forEach(s=>$(s).addEventListener('change',reload));
$('#search').addEventListener('input',reload);
$('#f-mincount').addEventListener('input',e=>{$('#mc-val').textContent=e.target.value;reload();});
$('#resetBtn').addEventListener('click',resetFilters);
$('#selAllPage').addEventListener('change',e=>selectAllPage(e.target.checked));
let rdeb; window.addEventListener('resize',()=>{ clearTimeout(rdeb); rdeb=setTimeout(()=>{ if(computePageSize()!==lastPS){ state.page=1; loadList(); } },300); });
$$('.tab').forEach(t=>t.addEventListener('click',()=>switchView(t.dataset.view)));
$('#exportCsvAll').addEventListener('click',()=>exportAll('csv'));
$('#exportJsonAll').addEventListener('click',()=>exportAll('json'));
$('#exportTablePdf').addEventListener('click',tablePdf);
$('#exportStatsPdf').addEventListener('click',statsPdf);
$('#selPdf').addEventListener('click',selectionPdf);
$('#selCsv').addEventListener('click',()=>exportSelection('csv'));
$('#selJson').addEventListener('click',()=>exportSelection('json'));
$('#selClear').addEventListener('click',()=>{state.sel.clear();$$('.card').forEach(c=>c.classList.remove('sel'));$('#selAllPage').checked=false;updateSelbar();});
$('#loginBtn').addEventListener('click',()=>{ if(state.pw){state.pw='';sessionStorage.removeItem('qe_pw');refreshLoginBtn();state.page=1;loadList();if(state.view==='stats')loadStatsView();toast('Abgemeldet.');}else $('#loginOverlay').classList.remove('hidden'); });
$('#refreshBtn').addEventListener('click',startRefresh);
$('#pwOk').addEventListener('click',doLogin);
$('#pwInput').addEventListener('keydown',e=>{if(e.key==='Enter')doLogin();});
$('#pwCancel').addEventListener('click',()=>$('#loginOverlay').classList.add('hidden'));
$('#overlay').addEventListener('click',e=>{if(e.target.id==='overlay')closeDetail();});

// ---- Rechtsseiten (Impressum / Datenschutz, in-App) -----------------------
function openLegal(which){
  const tpl=document.getElementById('tpl-'+which);
  if(!tpl) return;
  $('#legalBody').innerHTML = tpl.innerHTML;
  $('#legalOverlay').classList.remove('hidden');
  $('#legalBody').scrollTop=0;
}
function closeLegal(){ $('#legalOverlay').classList.add('hidden'); }
$$('[data-legal]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();openLegal(a.dataset.legal);}));
$('#legalClose').addEventListener('click',closeLegal);
$('#legalOverlay').addEventListener('click',e=>{if(e.target.id==='legalOverlay')closeLegal();});
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeLegal();});

refreshLoginBtn(); loadFilters(); loadList(); loadFreshness();
