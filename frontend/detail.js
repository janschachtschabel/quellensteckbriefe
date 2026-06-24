'use strict';
// detail.js — Detail-/Steckbrief-Ansicht.

// ---- Detail / Steckbrief --------------------------------------------------
async function openDetail(id){
  const r = await api('/api/sources/' + encodeURIComponent(id));
  $('#drawer').innerHTML = steckbrief(r);
  $('#overlay').classList.remove('hidden');
  $('#drawer .close').addEventListener('click', closeDetail);
  $('#sb-print')?.addEventListener('click', ()=>buildPdf([r], !!r.internal, pdfOpts()));
}
function closeDetail(){ $('#overlay').classList.add('hidden'); }
function provClass(p){ p=(p||'').toLowerCase(); if(p.includes('facet'))return 'facet'; if(p.includes('api'))return 'api'; if(p.includes('csv')||p.includes('crawler'))return 'csv'; return ''; }
function provTag(p){ return p?`<span class="prov ${provClass(p)}">${esc(p)}</span>`:''; }
const PUB_LABELS={'Faecher':'Fächer','URL':'URL'};
function kvRows(obj, prov){
  return Object.entries(obj).map(([k,v])=>{
    let val = Array.isArray(v)?v.join(', '):(v===true?'ja':v===false?'nein':esc(v));
    if(k==='OER'&&v===true) val='<span class="tag-oer">ja (OER)</span>';
    return `<div class="k">${esc(PUB_LABELS[k]||k)}</div><div class="v">${val} ${prov?provTag(prov[k]):''}</div>`;
  }).join('');
}
function fieldGenTable(fg){
  if(!fg.length) return '';
  const byItem={}; fg.forEach(f=>(byItem[f.item]??=[]).push(f));
  const rows=Object.entries(byItem).map(([item,fields])=>fields.map((f,i)=>`<tr>
    <td>${i===0?`<b>${esc(item)}</b>`:''}</td><td>${esc(f.field)}</td>
    <td>${f.aktiv?'✓ aktiv':esc(f.status)}</td><td class="how">${esc(f.how||(f.aktiv?'aus Quelldaten':''))}</td></tr>`).join('')).join('');
  return `<table class="fieldtable"><thead><tr><th>Item</th><th>Feld</th><th>Status</th><th>Erzeugung</th></tr></thead><tbody>${rows}</tbody></table>`;
}
const LIZENZ_KEYS=['Lizenz','OER','Urheber'];
const KI_KEYS=['robots.txt','TDM-Hinweis (§44b)','AGB/Nutzungsbedingungen','Lizenz-Check','API-Nutzungsbedingungen'];
const BILDUNG_KEYS=['Faecher','Bildungsstufen','Inhaltstypen','Zielgruppe','Alter','Sprachniveau','Zielsprache','Lehrplanbezug','FSK'];
function pick(obj,keys){ const o={}; keys.forEach(k=>{ if(k in obj) o[k]=obj[k]; }); return o; }

// Interner Bereich: Fakten zuerst (gruppiert), Bemerkungen zuletzt.
const INT_FACTS=['Erschliessungsstatus (genau)','Workflow-Status','Korrekturliste',
  'Node-ID','quelldatensatzProd','replicationsource','general_identifier','spider',
  'crawlerType','zustand','prio','haeufigkeit','prodLetzterCrawl','stagingLetzterCrawl','anzahlProd','anzahlStaging',
  'exportOerBerlin','github','Vertrag/Vereinbarung','Vereinbarung (alt)','zuletzt geaendert'];
const INT_REMARKS=['spiderBemerkungen','kiEinschaetzung','bemerkungStatus','hinweisQuelldatensatz'];
const INT_LABELS={
  'Erschliessungsstatus (genau)':'Erschließungsstatus','Workflow-Status':'Redaktions-/Workflow-Status',
  'Korrekturliste':'Korrekturliste','Node-ID':'Quelldatensatz (Node-ID)','quelldatensatzProd':'Quelldatensatz-Link (Prod)',
  'replicationsource':'replicationsource','general_identifier':'general_identifier','spider':'Spider',
  'crawlerType':'Crawler-Typ','zustand':'Betriebszustand','prio':'Priorität','haeufigkeit':'Crawl-Häufigkeit',
  'prodLetzterCrawl':'Letzter Crawl (Prod)','stagingLetzterCrawl':'Letzter Crawl (Staging)',
  'anzahlProd':'Anzahl Prod (Stand letzter Crawl)','anzahlStaging':'Anzahl Staging (Stand letzter Crawl)',
  'exportOerBerlin':'Export OER Berlin','github':'GitHub','zuletzt geaendert':'zuletzt geändert',
  'spiderBemerkungen':'Spider-Bemerkungen','kiEinschaetzung':'KI-/Erschließungs-Einschätzung',
  'bemerkungStatus':'Bemerkung/Status','hinweisQuelldatensatz':'Hinweis zum Quelldatensatz'};
function kvRowsLbl(entries){ return entries.map(([k,v])=>`<div class="k">${esc(INT_LABELS[k]||k)}</div><div class="v">${Array.isArray(v)?esc(v.join(', ')):esc(v)}</div>`).join(''); }
function internalBlock(o){
  const has=Object.keys(o).filter(k=>o[k]!==''&&o[k]!=null);
  const facts=INT_FACTS.filter(k=>has.includes(k)).map(k=>[k,o[k]]);
  const other=has.filter(k=>!INT_FACTS.includes(k)&&!INT_REMARKS.includes(k)).map(k=>[k,o[k]]);
  const rem=INT_REMARKS.filter(k=>has.includes(k)).map(k=>[k,o[k]]);
  let h=`<div class="kv">${kvRowsLbl(facts.concat(other))}</div>`;
  if(rem.length) h+=`<h4 class="sb-sub2">Bemerkungen</h4><div class="kv kv-remarks">${kvRowsLbl(rem)}</div>`;
  return h;
}
function steckbrief(r){
  const id=r.identity;
  const MARK={WLO_MIGRATION:['🔄 Datenmigration (WLO)','mig'],LEGACY_BINDUNG:['🏷️ Legacy-Bindung','leg'],
    TYP_NICHT_QUELLE:['⚠ Inhaltstyp ≠ Quelle','mis'],OER:['OER','oer'],ZWEITDATENSATZ:['Zweit-Datensatz','zw']};
  const marks=(r.flags||[]).filter(f=>MARK[f]).map(f=>`<span class="mk mk-${MARK[f][1]}">${MARK[f][0]}</span>`).join('');
  const head=`<div class="sb-head"><button class="close">×</button><h2>${esc(r.name)}</h2>
    <div class="sb-sub">${esc(r.kind)} · ${num(r.contentCount)} Inhalte · ${esc(r.erschliessung)}${id.bezugsquelle?` · Bezugsquelle: ${esc(id.bezugsquelle)}`:''}</div>
    ${marks?`<div class="sb-markers">${marks}</div>`:''}</div>`;
  const lizenz=pick(r.public,LIZENZ_KEYS), ki=pick(r.public,KI_KEYS), bildung=pick(r.public,BILDUNG_KEYS);
  const grundObj=pick(r.public, Object.keys(r.public).filter(k=>k!=='Titel'&&!LIZENZ_KEYS.includes(k)&&!KI_KEYS.includes(k)&&!BILDUNG_KEYS.includes(k)));
  const sGrund=`<div class="sb-section"><h3>📋 Grund-Informationen</h3><div class="kv">${kvRows(grundObj,r.provenance)}</div></div>`;
  const sBildung=Object.keys(bildung).length?`<div class="sb-section"><h3>🎓 Bildung &amp; Einordnung</h3><div class="kv">${kvRows(bildung,r.provenance)}</div></div>`:'';
  const sLizenz=Object.keys(lizenz).length?`<div class="sb-section"><h3>📄 Lizenz</h3><div class="kv">${kvRows(lizenz,r.provenance)}</div></div>`:'';
  const q=r.quality||{};
  const sQuality=Object.keys(q).length?`<div class="sb-section"><h3>⭐ Qualitätsmerkmale</h3>
    <p class="hint">Nur redaktionell gepflegte Felder (aus den Quelldatensatz-Metadaten).</p>
    <div class="kv">${Object.entries(q).map(([k,v])=>`<div class="k">${esc(k)}</div><div class="v">${esc(v)} <span class="prov api">WLO-API</span></div>`).join('')}</div></div>`:'';
  const sFelder=r.fieldGeneration.length?`<div class="sb-section"><h3>🛠️ Metadaten-Erzeugung (Crawler-Provenienz)</h3>
    <p class="hint">${r.fieldActiveCount} aktive Felder — je Feld ob/wie es der Crawler erzeugt (gescraped, hard-coded, gemappt …).</p>${fieldGenTable(r.fieldGeneration)}</div>`:'';
  const sInternal=r.internal?`<div class="sb-section internal"><h3>🔒 Interne Infos (Team)</h3>${internalBlock(r.internal)}
    ${r.flags?.length?`<p class="hint">Flags: ${r.flags.map(esc).join(', ')}</p>`:''}</div>`
    :(r.hasInternal?`<div class="sb-section"><div class="locked">🔒 Interne Crawler-Vermerke &amp; genauer Status nur mit Team-Login sichtbar.</div></div>`:'');
  const sKi=Object.keys(ki).length?`<div class="sb-section ki-section"><h3>⚖️ KI-Nutzung &amp; Recht</h3>
    <p class="hint">Rechts-/Nutzungshinweise der Quelle selbst — Basis der KI-Nutzungs-Einschätzung. (Ob WLO einen Vertrag hat, steht nur im internen Bereich.)</p>
    <div class="kv">${kvRows(ki,r.provenance)}</div></div>`:'';
  const actions=`<div class="print-actions"><button id="sb-print" class="btn">🖨️ Steckbrief als PDF</button>
    ${id.url?`<a class="btn-ghost" href="${esc(id.url)}" target="_blank" rel="noopener">↗ Quelle öffnen</a>`:''}</div>`;
  return head+`<div class="sb-body">${actions}${sGrund}${sBildung}${sLizenz}${sQuality}${sFelder}${sKi}${sInternal}</div>`;
}
