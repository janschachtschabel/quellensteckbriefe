'use strict';
// export.js — CSV/JSON export (filter & selection).

// ---- Export (CSV/JSON) ----------------------------------------------------
function exportAll(fmt){ window.location.href = `/api/export.${fmt}?` + filterParams().toString(); }
// Team-only data-problem protocol (Markdown); the team session cookie authorizes the download.
function exportProtokoll(){ window.location.href = '/api/protokoll.md'; }
async function exportSelection(fmt){
  if(!state.sel.size) return;
  const d = await apiPost('/api/sources/batch', {ids:[...state.sel]});
  const flat = d.items.map(r=>({id:r.id,name:r.name,kind:r.kind,bezugsquelle:r.identity.bezugsquelle,nodeId:r.identity.nodeId,
    spider:r.identity.spider,contentCount:r.contentCount,erschliessung:r.erschliessung,url:r.public.URL||'',
    Lizenz:r.public.Lizenz||'',OER:r.public.OER?'ja':'',Faecher:(r.public.Faecher||[]).join(' | '),
    Bildungsstufen:(r.public.Bildungsstufen||[]).join(' | '),Sprache:r.public.Sprache||'',fieldActiveCount:r.fieldActiveCount}));
  if(fmt==='json'){ dl(new Blob([JSON.stringify(flat,null,2)],{type:'application/json'}),'auswahl.json'); }
  else { const cols=Object.keys(flat[0]||{id:1}); const csv='﻿'+[cols.join(';'),...flat.map(r=>cols.map(c=>`"${String(r[c]??'').replace(/"/g,'""')}"`).join(';'))].join('\n'); dl(new Blob([csv],{type:'text/csv'}),'auswahl.csv'); }
  toast(`${flat.length} Quellen exportiert.`);
}
function dl(blob,name){ const u=URL.createObjectURL(blob);const a=document.createElement('a');a.href=u;a.download=name;a.click();URL.revokeObjectURL(u); }
