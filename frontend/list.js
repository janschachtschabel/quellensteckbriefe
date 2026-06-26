'use strict';
// list.js — filters, source list/tiles, selection, card action menu.

// ---- Filters / query ------------------------------------------------------
function filterParams(){
  const p = new URLSearchParams();
  const q=$('#search').value.trim(); if(q) p.set('q',q);
  // Source type (end user). Structural — complete sets, crawlers are NOT
  // filtered out (a crawler with a Quelldatensatz also counts under "… and Bezugsquelle").
  const art=$('#f-art').value;
  if(art==='crawler') p.set('has_spider','true');                                    // sources with a crawler (all Spider-bound)
  else if(art==='node') p.set('has_node','true');                                    // with Quelldatensatz (all with a record)
  else if(art==='bq') p.set('has_bezugsquelle','true');                              // with Bezugsquelle (all with a Bezugsquelle)
  else if(art==='both'){ p.set('has_node','true'); p.set('has_bezugsquelle','true'); } // Quelldatensatz and Bezugsquelle
  // Review/origin filter — team only (sets ONE criterion, does not collide with "Source type").
  const pruef=$('#f-pruef') ? $('#f-pruef').value : '';
  if(pruef==='wlo') p.set('flag','WLO_MIGRATION');             // data migration = WLO_MIGRATION flag (1:1 with the protocol rubric)
  else if(pruef==='legacy') p.set('flag','LEGACY_BINDUNG');    // bound via old tagging
  else if(pruef==='mistyp') p.set('flag','TYP_NICHT_QUELLE');  // record without type "Quelle"
  else if(pruef==='blacklist') p.set('flag','BLACKLIST');      // sorted out (otherwise hidden)
  else if(pruef==='zweit') p.set('flag','ZWEITDATENSATZ');     // secondary dataset (otherwise hidden)
  else if(pruef==='einzel') p.set('flag','BQ_EINZELINHALT');   // Bezugsquelle facet entry with a single content item
  else if(pruef==='duenn') p.set('flag','METADATEN_DUENN');    // source dataset missing core metadata fields
  else if(pruef==='bindung') p.set('flag','BINDUNG_UNVOLLSTAENDIG'); // crawler binding without a source dataset
  else if(pruef==='fehltag') p.set('flag','FEHLTAGGING');       // mixed content types (Quelle + others)
  else if(pruef==='dublette') p.set('flag','DUBLETTE_VERDACHT'); // shares URL/title with another record
  else if(pruef==='qdohnebq') p.set('flag','QD_OHNE_BEZUGSQUELLE'); // source dataset without a Bezugsquelle
  else if(pruef==='bqohneqd') p.set('flag','BQ_OHNE_QD');          // publisher Bezugsquelle with content but no source dataset
  else if(pruef==='ohnestatus') p.set('flag','OHNE_STATUS');       // source dataset without editorial status
  else if(pruef==='statusink') p.set('flag','STATUS_INKONSISTENT'); // fully filled, but editorial status < 9
  else if(pruef==='nichtpub') p.set('flag','NICHT_PUBLIZIERT');    // not published in search
  else if(pruef==='spideruneindeutig') p.set('flag','SPIDER_UNEINDEUTIG'); // general_identifier != replicationsource
  const subj=$('#f-subject').value; if(subj) p.set('subject',subj);
  const lvl=$('#f-level').value; if(lvl) p.set('level',lvl);
  const lrt=$('#f-lrt').value; if(lrt) p.set('lrt',lrt);
  const lic=$('#f-license').value; if(lic) p.set('license',lic);
  const lang=$('#f-language').value; if(lang) p.set('language',lang);
  const mc=+$('#f-mincount').value; if(mc) p.set('min_count',mc);
  if($('#f-oer').checked) p.set('oer','true');
  if($('#f-fp').checked) p.set('only_field_profile','true');
  return p;
}

async function loadFilters(){
  const f = await api('/api/meta/filters');
  const opt=(a)=>'<option value="">alle</option>'+a.map(s=>`<option>${esc(s)}</option>`).join('');
  $('#f-subject').innerHTML = opt(f.subjects);
  $('#f-level').innerHTML = opt(f.levels);
  $('#f-lrt').innerHTML = opt(f.lrts||[]);
  $('#f-license').innerHTML = opt(f.licenses||[]);
  $('#f-language').innerHTML = opt(f.languages||[]);
}

let lastPS = 12;
function computePageSize(){
  // Exactly 4 rows of tiles per page (column count from width + CSS min 335px, gap 16px)
  const list = $('#list');
  const w = (list && list.clientWidth) || window.innerWidth || 1000;
  const cols = Math.max(1, Math.floor((w + 16) / (335 + 16)));
  return cols * 4;
}
async function loadList(){
  const p = filterParams();
  const [sf,so]=($('#f-sort').value||'contentCount|desc').split('|');
  p.set('sort',sf); p.set('order',so);
  lastPS = computePageSize();
  p.set('page', state.page); p.set('page_size', lastPS);
  const d = await api('/api/sources?' + p.toString());
  // The "hidden" breakdown is shown ONLY in the top-right header info text, so that
  // display differences vs. the API stay traceable; this list shows only the result count.
  $('#resultCount').textContent = `${num(d.total)} Treffer`;
  const h = d.hidden || {total: 0, blacklist: 0, zweitDatensatz: 0};
  const parts = [];
  if (h.blacklist) parts.push(`${num(h.blacklist)} aussortiert`);
  if (h.zweitDatensatz) parts.push(`${num(h.zweitDatensatz)} Mehrfach-Datensätze`);
  const note = h.total ? ` · ${num(h.total)} ausgeblendet${parts.length ? ` (${parts.join(' + ')})` : ''}` : '';
  const eh = $('#exportHint');
  eh.textContent = `${num(d.total)} im Filter${note}`;
  eh.title = h.total
    ? 'Im aktuellen Filter nicht angezeigt. „aussortiert" = Blacklist (Nicht-Quellen); „Mehrfach-Datensätze" = weitere Quelldatensätze derselben Bezugsquelle (zählen unter ihrer Bezugsquelle; in der Quelldatensatz-Ansicht sichtbar, im Team-Filter „Datenprüfung" abrufbar). angezeigt + ausgeblendet = im Filter insgesamt.'
    : '';
  $('#list').innerHTML = d.items.map(card).join('') || '<p class="hint">Keine Treffer.</p>';
  d.items.forEach(it => {
    const el=$(`.card[data-id="${cssEsc(it.id)}"]`);
    el?.addEventListener('click', (e)=>{ if(e.target.closest('.card-menu-btn')||e.target.closest('.card-check'))return; openDetail(it.id); });
    $(`.card-menu-btn[data-id="${cssEsc(it.id)}"]`)?.addEventListener('click',(e)=>{ e.stopPropagation(); openCardMenu(e.currentTarget, it.id); });
    const cb=$(`.card-check[data-id="${cssEsc(it.id)}"]`);
    cb?.addEventListener('click', e=>e.stopPropagation());
    cb?.addEventListener('change', ()=>toggleSel(it.id, cb.checked));
  });
  $('#selAllPage').checked = d.items.length>0 && d.items.every(it=>state.sel.has(it.id));
  renderPager(d);
}
const cssEsc = (s) => String(s).replace(/["\\]/g, '\\$&');   // escape " and \ for [data-id="…"]

const KIND={crawler:['🕸️','Crawler-Quelle'],manuell:['✍️','Redaktionelle Quelle'],bezugsquelle:['🏷️','Bezugsquelle']};
function card(it){
  const [ic,lbl]=KIND[it.kind]||['',it.kind];
  const desc=it.public.Beschreibung || it.erschliessung || '';
  const thumb = it.previewUrl ? `<div class="thumb"><img src="${esc(it.previewUrl)}" loading="lazy" referrerpolicy="no-referrer" onerror="this.closest('.thumb').remove()">
      <div class="thumb-badges">${it.flags.includes('OER')?'<span class="b-oer">OER</span>':''}</div></div>`:'';
  // Unified status pills: color = status (green ok / yellow limitation / red missing / gray unknown).
  const node=it.identity.nodeId, bq=it.identity.bezugsquelle, sp=it.identity.spider;
  const misTyp=it.flags.includes('TYP_NICHT_QUELLE'), isLegacy=it.flags.includes('LEGACY_BINDUNG');
  const spName=it.identity.spiderVocabName||(sp||'').replace(/_spider$/,'');
  const migNote=it.flags.includes('WLO_MIGRATION')?' · über WLO-Datenmigration eingespielt':'';
  let qdSt,qdInfo;
  if(node&&!misTyp){qdSt='ok';qdInfo='Quelldatensatz vorhanden – Inhaltstyp = Quelle';}
  else if(node){qdSt='warn';qdInfo='Quelldatensatz vorhanden, aber Inhaltstyp ≠ Quelle (Korrektur-Kandidat)';}
  else {qdSt='unk';qdInfo='Kein Quelldatensatz erfasst (evtl. such-versteckt)';}
  const bqSt=bq?'ok':'miss', bqInfo=bq?('Bezugsquelle: '+bq):'Keine Bezugsquelle hinterlegt';
  let spSt,spInfo;
  if(sp){spSt=isLegacy?'warn':'ok';spInfo=(isLegacy?'Legacy-Vocab-Bindung: ':'Crawler-Bindung: ')+spName;}
  else if(node){spSt='miss';spInfo='Keine Crawler-/Spider-Bindung';}
  else {spSt='unk';spInfo='Spider-Bindung unbekannt';}
  const pill=(label,st,info)=>`<span class="badge st-${st}" title="${esc(info)}">${label}</span>`;
  const fb=[
    pill('🗂 QD', qdSt, qdInfo+migNote),
    pill('🏷 BQ', bqSt, bqInfo),
    pill('🕸 Spider', spSt, spInfo+migNote),
    it.flags.includes('ZWEITDATENSATZ')?pill('Zweit','warn','Zweit-Datensatz derselben Bezugsquelle (zählt keine zusätzlichen Inhalte)'):'',
    it.fieldActiveCount?`<span class="badge st-count" title="${it.fieldActiveCount} aktive Metadatenfelder (Crawler-Provenienz)">${it.fieldActiveCount} F</span>`:'',
  ].join('');
  return `<div class="card ${state.sel.has(it.id)?'sel':''}" data-id="${esc(it.id)}">
    <div class="card-head">
      <input type="checkbox" class="card-check" data-id="${esc(it.id)}" title="zur Auswahl hinzufügen" ${state.sel.has(it.id)?'checked':''}>
      <span class="ctype">${ic} ${esc(lbl)}</span>
      <button class="card-menu-btn" data-id="${esc(it.id)}" title="weitere Aktionen">⋮</button>
    </div>
    <h4>${esc(it.name)}</h4>
    <div class="card-body"><p class="desc">${esc(desc)}</p>${thumb}</div>
    <div class="card-foot"><span class="fcount">${num(it.contentCount)} Inhalte</span>
      <span class="foot-badges">${fb}</span></div>
  </div>`;
}

function renderPager(d){
  const b=(lbl,pg,dis)=>`<button class="btn-ghost small" ${dis?'disabled':''} data-pg="${pg}">${lbl}</button>`;
  $('#pager').innerHTML = d.pages>1 ? b('‹ zurück',d.page-1,d.page<=1)+`<span class="hint">Seite ${d.page} / ${d.pages}</span>`+b('weiter ›',d.page+1,d.page>=d.pages) : '';
  $$('#pager [data-pg]').forEach(el=>el.addEventListener('click',()=>{state.page=+el.dataset.pg;loadList();window.scrollTo(0,0);}));
}

// ---- Selection ------------------------------------------------------------
function toggleSel(id, on){
  if(on) state.sel.add(id); else state.sel.delete(id);
  $(`.card[data-id="${cssEsc(id)}"]`)?.classList.toggle('sel', on);
  updateSelbar();
}
function updateSelbar(){
  const n = state.sel.size;
  $('#selCount').textContent = n;
  $('#selbar').classList.toggle('hidden', n===0);
}
function selectAllPage(on){
  $$('.card').forEach(c=>{ const id=c.dataset.id; if(on)state.sel.add(id);else state.sel.delete(id); c.classList.toggle('sel',on); });
  updateSelbar();
}

// ---- Card action menu -----------------------------------------------------
let menuId=null;
function openCardMenu(btn, id){
  menuId=id;
  const m=$('#cardmenu'), r=btn.getBoundingClientRect();
  m.classList.remove('hidden');
  m.style.top=(window.scrollY+r.bottom+4)+'px';
  m.style.left=(window.scrollX+Math.min(r.right-210, window.innerWidth-220))+'px';
  m.querySelector('[data-act="select"]').textContent = state.sel.has(id)?'✗ Aus Auswahl entfernen':'✓ Zur Auswahl';
}
function closeCardMenu(){ $('#cardmenu').classList.add('hidden'); menuId=null; }
$('#cardmenu').addEventListener('click', async (e)=>{
  const act=e.target.closest('button')?.dataset.act; if(!act||!menuId) return;
  const id=menuId; closeCardMenu();
  if(act==='detail') openDetail(id);
  else if(act==='select') toggleSel(id, !state.sel.has(id));
  else if(act==='open'){ const r=await api('/api/sources/'+encodeURIComponent(id)); const u=safeUrl(r.identity.url); if(u) window.open(u,'_blank','noopener'); else toast('Keine (gültige) URL hinterlegt.'); }
  else if(act==='pdf'){ const r=await api('/api/sources/'+encodeURIComponent(id)); buildPdf([r], !!r.internal, pdfOpts()); }
});
document.addEventListener('click',(e)=>{ if(!e.target.closest('#cardmenu')&&!e.target.closest('.card-menu-btn')) closeCardMenu(); });
