'use strict';
// stats.js — Statistik-Ansicht (oeffentlich + Team) mit Charts.

// Balkengruppe auf EINER gemeinsamen Skala (Größenverhältnisse vergleichbar).
// rows: [{label, value, color, title?}]. opts.max überschreibt die Auto-Skala.
function statBarGroup(title, rows, opts){
  opts = opts || {};
  const max = opts.max || Math.max(1, ...rows.map(r => r.value || 0));
  const body = rows.map(r => `<div class="barrow"><span class="bl" title="${esc(r.title||r.label)}">${r.label}</span><span class="bar" style="width:${Math.round((r.value||0)/max*100)}%;background:${r.color||'var(--primary)'}"></span><span class="bv">${num(r.value||0)}</span></div>`).join('');
  return `<div class="chart-card ${opts.cls||''}"><h3>${esc(title)}</h3><div class="barlist">${body}</div>${opts.hint?`<p class="hint">${opts.hint}</p>`:''}</div>`;
}

// ---- Statistik-View (öffentlich) ------------------------------------------
async function loadStatsView(){
  const s = await api('/api/stats/full');
  state.lastStats = s;
  state.charts.forEach(c=>c.destroy()); state.charts=[];
  const t=s.totals, fg=s.fieldGeneration, cc=s.contentCoverage,
        inh=s.inhalte||{};
  const head=(txt,sub)=>`<div class="stats-head">${txt}${sub?`<span> · ${sub}</span>`:''}</div>`;
  const card=(id,title,cls='')=>`<div class="chart-card ${cls}"><h3>${title}</h3><canvas id="${id}"></canvas></div>`;
  const barlist=(title,items,color)=>{ if(!items||!items.length) return '';
    const max=Math.max(1,...items.map(i=>i.count));
    return `<div class="chart-card"><h3>${title}</h3><div class="barlist">${items.map(i=>`<div class="barrow"><span class="bl" title="${esc(i.value)}">${esc(i.value)}</span><span class="bar" style="width:${Math.round(i.count/max*100)}%;background:${color}"></span><span class="bv">${num(i.count)}</span></div>`).join('')}</div></div>`; };
  // Füllstand je Metadatenfeld: Anteil der Crawler, die das Feld erzeugen (0–100 %).
  const fuellPublic=(title, items, basis)=>{ if(!items||!items.length) return '';
    const rows=items.map(i=>{ const p=Math.round((i.count||0)/Math.max(1,basis)*100);
      return `<div class="barrow"><span class="bl" title="${esc(i.value)}">${esc(i.value)}</span><span class="bar" style="width:${p}%;background:#0a7c8a"></span><span class="bv">${p}%</span></div>`; }).join('');
    return `<div class="chart-card tall"><h3>${title}</h3><p class="hint">Anteil der ${num(basis)} Crawler-Quellen, die das Feld erzeugen.</p><div class="barlist">${rows}</div></div>`; };
  const covTypeCard=()=>{ const items=[['mit Bezugsquelle',cc.bezugsquelle],['über Crawler',cc.crawler],['mit Quelldatensatz',cc.quelldatensatz]]; const max=Math.max(1,...items.map(i=>i[1]));
    return `<div class="chart-card wide"><h3>Inhaltsabdeckung nach Quellentyp</h3><div class="barlist">${items.map(([l,n])=>`<div class="barrow"><span class="bl">${l}</span><span class="bar" style="width:${Math.round(n/max*100)}%;background:var(--primary)"></span><span class="bv">${num(n)}</span></div>`).join('')}</div><p class="hint">Wie viele Inhalte je Quellentyp erreichbar sind. Die Gruppen überlappen sich (ein Inhalt kann zugleich einen Crawler und eine Bezugsquelle haben).</p></div>`; };
  // Quellenverwaltung: gleiche Zählweise wie der Filter „Art der Quelle"
  // (sichtbare Records ohne Blacklist, Record-Zahlen) — damit Stats == Filter.
  const qv = s.quellenverwaltung || {};
  const profilCard = statBarGroup('Quellenverwaltung', [
    {label:'alle Quellen', value:qv.gesamt||0, color:'var(--primary)', title:'sichtbare Quellen (ohne aussortierte)'},
    {label:'mit Quelldatensatz', value:qv.mitQuelldatensatz||0, color:'#2e6ca8', title:'Quellen mit eigenem Datensatz (ccm:io)'},
    {label:'mit Bezugsquelle', value:qv.mitBezugsquelle||0, color:'#1a8a4d', title:'Quellen mit hinterlegter Bezugsquelle'},
    {label:'davon Überschneidung', value:qv.ueberschneidung||0, color:'#a85b00', title:'haben Quelldatensatz UND Bezugsquelle'},
  ], {cls:'wide', hint:'Anzahl sichtbarer Quellen (aussortierte ausgeblendet) — die Balken sind deckungsgleich mit dem Filter „Art der Quelle". „Überschneidung" = Quellen mit Quelldatensatz UND Bezugsquelle.'});

  // Top-Listen: füllen die Breite (umbrechende Reihe, KEIN horizontales Scrollen).
  // Top-Crawler & Inhaltstypen entfernt — Inhaltstypen wandern als Fehleranalyse
  // in den Team-Bereich.
  const topLists = [
    ['Top-Quellen nach Inhalten', s.topByContent.slice(0,10).map(c=>({value:c.name,count:c.count})),'var(--primary)'],
    ['Top-Fächer', s.topSubjects.slice(0,10),'var(--accent2)'],
    ['Top-Lizenzen', s.licenseDistribution.slice(0,10),'var(--accent)'],
    ['Top-Bildungsstufen', s.topLevels.slice(0,10),'#1a8a4d'],
    ['Top-Sprachen', s.topLanguages.slice(0,10),'#5b3bb8'],
  ];
  const lists = `<div class="chart-grid lists">${topLists.map(([ti,it,c])=>barlist(ti,it,c)).join('')}</div>`;

  $('#view-stats').innerHTML =
      head('Top-Listen','die größten je Dimension')
    + lists
    + head('Quellen & Herkunft')
    + `<div class="chart-grid">` + profilCard + `</div>`
    + head('Inhalte & Abdeckung', `${num(inh.wloProd||t.inhalteGesamt)} Inhalte gesamt · ${num(inh.zuordenbar!=null?inh.zuordenbar:t.inhalteGesamt)} einer Quelle zuordenbar`)
    + `<div class="chart-grid">` + covTypeCard() + `</div>`
    + `<div class="chart-grid cols2">`
      + card('c-brk-node','Quellen × Inhalte (je Quelldatensatz)','tall')
      + card('c-bqsize','Bezugsquellen × Inhalte','tall')
    + `</div>`
    + head('Metadaten & Crawler','Feld-Füllstände, Daten-Herkunft und Crawler-Typen')
    + `<div class="chart-grid cols3">`
      + fuellPublic('Füllstand Metadatenfelder', fg.fieldActivity, fg.crawlerWithProfile)
      + card('c-method','Daten-Herkunft','tall')
      + card('c-ctype','Crawler nach Typ','tall')
    + `</div>`;

  const C=window.Chart;
  if(C){
    const mk=(id,cfg)=>{const el=$('#'+id);if(el)state.charts.push(new C(el,cfg));};
    const PIE=['#003b7c','#ec4a70','#f97316','#1a8a4d','#5b3bb8','#0a7c8a','#b8860b','#9aa7bd','#c0392b','#4682b4'];
    const dough=(id,labels,data)=>mk(id,{type:'doughnut',data:{labels,datasets:[{data,backgroundColor:PIE}]},options:{plugins:{legend:{position:'bottom',labels:{boxWidth:12,font:{size:10}}}}}});
    mk('c-brk-node',{type:'bar',data:{labels:(s.contentBracketsNode||[]).map(b=>b.value),datasets:[{data:(s.contentBracketsNode||[]).map(b=>b.count),backgroundColor:'#003b7c'}]},options:{plugins:{legend:{display:false}}}});
    mk('c-bqsize',{type:'bar',data:{labels:s.bqSizeBrackets.map(b=>b.value),datasets:[{data:s.bqSizeBrackets.map(b=>b.count),backgroundColor:'#ec4a70'}]},options:{plugins:{legend:{display:false}}}});
    dough('c-ctype',(s.crawlerByType||[]).map(x=>x.value),(s.crawlerByType||[]).map(x=>x.count));
    dough('c-method',fg.byMethod.map(m=>m.value),fg.byMethod.map(m=>m.count));
  }
  if(state.pw) await loadTeamStats();
}

// ---- Team-Statistik (nur mit Team-Login) ----------------------------------
async function loadTeamStats(){
  let d; try{ d=await api('/api/stats/team'); }catch{ return; }
  const h=d.herkunft, pr=d.probleme, sb=d.spiderBindung||{}, ff=d.feldFuellstand||{metadaten:[],ki:[]};
  const sf=state.lastStats||{};   // öffentliche Vollstatistik (Korrektur + Inhaltstypen)
  const head=(txt,sub)=>`<div class="stats-head team">${txt}${sub?`<span> · ${sub}</span>`:''}</div>`;
  const dupCard=(o,title,hint)=>`<div class="chart-card"><h3>${title}</h3>
    <p class="hint">${num(o.gruppen)} Gruppen · ${num(o.ueberzaehlig)} überzählige Datensätze. ${hint||''}</p>
    <div class="barlist">${(o.beispiele||[]).map(b=>`<div class="barrow"><span class="bl" title="${esc(b.wert)}">${esc(b.wert||'(leer)')}</span><span class="bar" style="width:${Math.min(100,b.anzahl*18)}%;background:var(--bad)"></span><span class="bv">${b.anzahl}×</span></div>`).join('')||'<span class="hint">keine</span>'}</div></div>`;
  const fuellbar=(title,items,basis,color)=>{ if(!items||!items.length) return '';
    const rows=items.map(i=>`<div class="barrow"><span class="bl" title="${esc(i.feld)}">${esc(i.feld)}</span><span class="bar" style="width:${i.prozent}%;background:${color}"></span><span class="bv">${i.prozent}%</span></div>`).join('');
    return `<div class="chart-card"><h3>${title}</h3><p class="hint">Anteil mit gefülltem Feld · Basis ${num(basis)}.</p><div class="barlist">${rows}</div></div>`; };

  // Korrekturliste (kuratiert) — aus der öffentlichen Statistik, hier im Team-Bereich
  const korrekturCard=(()=>{ const k=sf.korrektur||{}; const wl=k.whitelist||0, bl=k.blacklist||0, mx=Math.max(1,wl,bl);
    const row=(l,c,v)=>`<div class="barrow"><span class="bl">${l}</span><span class="bar" style="width:${Math.round(v/mx*100)}%;background:${c}"></span><span class="bv">${num(v)}</span></div>`;
    return `<div class="chart-card"><h3>Korrekturliste (kuratiert)</h3>
      <p class="hint">Manuell gepflegt. <b>Whitelist</b> = gesichert korrekt. <b>Blacklist</b> = mögliche Dublette / kein echter Datensatz (herausgerechnet, <b>nicht gelöscht</b>).</p>
      <div class="barlist">${row('Whitelist','#1a8a4d',wl)}${row('Blacklist','#ec4a70',bl)}</div>
      <p class="hint">In der Schnittmenge herausgerechnet: ${num(k.whitelistImSchnitt||0)} Whitelist · ${num(k.blacklistImSchnitt||0)} Blacklist.</p></div>`; })();
  // Inhaltstypen der Quelldatensätze — Fehleranalyse (sollte „Quelle" sein)
  const lrtCard=(()=>{ const items=(sf.topLrt||[]).slice(0,15); if(!items.length) return '';
    const max=Math.max(1,...items.map(i=>i.count));
    return `<div class="chart-card"><h3>Inhaltstypen der Quelldatensätze – Fehleranalyse</h3>
      <p class="hint">Ein Quelldatensatz sollte den Typ „Quelle" tragen. Andere Typen (Webseite, Video …) deuten auf Mis-Tagging.</p>
      <div class="barlist">${items.map(i=>`<div class="barrow"><span class="bl" title="${esc(i.value)}">${esc(i.value)}</span><span class="bar" style="width:${Math.round(i.count/max*100)}%;background:#2e6ca8"></span><span class="bv">${num(i.count)}</span></div>`).join('')}</div></div>`; })();
  // Provenienz-Marker (technisch) — am Steckbrief als Badge, hier als Team-Übersicht
  const pv=sf.provenienz||{};
  const provCard = statBarGroup('Herkunft & Bindung (Marker)', [
    {label:'🔄 aus Datenübernahme (Migration)', value:pv.wloMigration||0, color:'#0a7c8a'},
    {label:'🏷️ über alte Verschlagwortung (Legacy)', value:pv.legacyBindung||0, color:'#a85b00'},
    {label:'⚠ mis-getaggt (Typ ≠ Quelle)', value:pv.misGetaggt||0, color:'#c0392b'},
  ], {hint:'Technische Provenienz — filterbar über „Prüfung/Herkunft (Team)", am Steckbrief als Badge.'});

  // Herleitung der Schnittmenge (Team-only, fokussiert auf die Bereinigung)
  const derivCard=(()=>{ const tot=h.schnittmenge_QuelldatensatzUndBezugsquelle||0, sauber=h.schnittmenge_sauber||0, zweit=h.schnittmenge_zweitDatensatz||0, black=h.schnittmenge_blacklist||0;
    const seg=(l,c,v)=>`<span class="seg" style="width:${(v/Math.max(1,tot)*100).toFixed(1)}%;background:${c}" title="${l}: ${num(v)}"></span>`;
    return `<div class="chart-card wide"><h3>🔒 Herleitung: Quelldatensatz UND Bezugsquelle</h3>
      <p class="hint"><b>${num(tot)}</b> Quelldatensätze tragen zugleich eine Bezugsquelle.</p>
      <div class="segbar">${seg('saubere Erst-Zuordnung','#1a8a4d',sauber)}${seg('Zweit-Datensätze','#9aa7bd',zweit)}${seg('Blacklist','#ec4a70',black)}</div>
      <div class="seglegend">
        <span><i style="background:#1a8a4d"></i>saubere Erst-Zuordnung ${num(sauber)}</span>
        <span><i style="background:#9aa7bd"></i>Zweit-Datensätze (gleiche BQ) ${num(zweit)}</span>
        <span><i style="background:#ec4a70"></i>Blacklist (mögliche Dublette) ${num(black)}</span>
      </div>
      <p class="hint">Herleitung des „bereinigten" Werts: <b>${num(tot)}</b> − ${num(black)} Blacklist − ${num(zweit)} Zweit-Datensätze = <b>${num(sauber)}</b> (≈ frühere Größenordnung „~660–700"). Nichts gelöscht – nur herausgerechnet.</p></div>`; })();

  // Spider-/Quell-Bindung — kombiniert: Kennzahlen als Balken + „nur rs"-Aufschlüsselung + Regel
  const bindCard=(()=>{ const max=Math.max(1, sb.mitReplicationsource||0, sb.echteBindungGesamt||0, sb.mitGeneralIdentifier||0, sb.beide||0);
    const bar=(l,v,c)=>`<div class="barrow"><span class="bl" title="${esc(l)}">${l}</span><span class="bar" style="width:${Math.round((v||0)/max*100)}%;background:${c}"></span><span class="bv">${num(v||0)}</span></div>`;
    const tot=Math.max(1,sb.nurReplicationsource||0);
    const seg=(l,c,v)=>`<span class="seg" style="width:${((v||0)/tot*100).toFixed(1)}%;background:${c}" title="${l}: ${num(v||0)}"></span>`;
    return `<div class="chart-card wide"><h3>Spider-/Quell-Bindung — wer bindet die Quelle?</h3>
      <div class="barlist">
        ${bar('mit general_identifier (saubere Bindung)', sb.mitGeneralIdentifier, '#1a8a4d')}
        ${bar('mit replicationsource', sb.mitReplicationsource, '#2e6ca8')}
        ${bar('beide gesetzt – alle unterschiedlich', sb.beide, '#a85b00')}
        ${bar('echte Bindung gesamt (gi ODER rs≠WLO)', sb.echteBindungGesamt, '#003b7c')}
      </div>
      <p class="hint" style="margin-top:.7rem">Davon <b>${num(sb.nurReplicationsource||0)}</b> Quellen <b>nur</b> mit replicationsource (kein general_identifier) — aufgeschlüsselt:</p>
      <div class="segbar">${seg('reine WLO-Migration','#ec4a70',sb.nurRs_wloMigration)}${seg('echter Spider','#1a8a4d',sb.nurRs_echterSpider)}${seg('Legacy-Vocab-Quelle','#2e6ca8',sb.nurRs_legacyName)}</div>
      <div class="seglegend">
        <span><i style="background:#ec4a70"></i>reine WLO-Migration ${num(sb.nurRs_wloMigration||0)}</span>
        <span><i style="background:#1a8a4d"></i>echter Spider, nur via rs ${num(sb.nurRs_echterSpider||0)}</span>
        <span><i style="background:#2e6ca8"></i>Legacy-Vocab-Quelle ${num(sb.nurRs_legacyName||0)}</span>
      </div>
      <p class="hint"><b>Filter-Regel:</b> echte Bindung = <code>general_identifier</code> ODER <code>replicationsource ≠ wirlernenonline_spider</code> = <b>${num(sb.echteBindungGesamt||0)}</b> Quellen (statt nur ${num(sb.mitGeneralIdentifier||0)} über general_identifier allein).</p></div>`; })();

  // Datenprobleme als breite Balkengrafik (nach Häufigkeit; kleine Werte zeigen die Zahl rechts)
  const problemeCard = statBarGroup('Datenprobleme', [
    {label:'Bezugsquellen < 5 Inhalte', value:pr.bezugsquellenUnter5Inhalte, color:'#c0392b'},
    {label:'Bezugsquellen mit 1 Inhalt', value:pr.bezugsquellenMit1Inhalt, color:'#c0392b'},
    {label:'Zweit-Datensätze (gleiche BQ)', value:pr.zweitDatensaetze, color:'#e0703a'},
    {label:'Mehrfach-Inhaltstypen (Fehltagging)', value:pr.mehrfachInhaltstypen_fehltagging, color:'#e0703a'},
    {label:'Blacklist-Einträge', value:pr.blacklistEintraege, color:'#e0a05a'},
    {label:'doppelte Titel', value:pr.doppelteTitel.ueberzaehlig, color:'#e0a05a'},
    {label:'unsichtbare Crawler-Quellen', value:pr.unsichtbareQuellenMitCrawler, color:'#9aa7bd'},
    {label:'doppelte URLs', value:pr.doppelteUrl.ueberzaehlig, color:'#9aa7bd'},
  ], {cls:'wide', hint:'Auffälligkeiten zur Bereinigung, nach Häufigkeit. Bei sehr kleinen Werten zählt die Zahl rechts.'});

  const html =
    head('🔒 Spider-/Quell-/Bezugsquellen-Bindung (Team)','wie Quellen gebunden sind')
    + `<div class="chart-grid">` + bindCard + derivCard + `</div>`
    + head('🔒 Datenprobleme (Team)','harte Auffälligkeiten zur Bereinigung')
    + `<div class="chart-grid">` + problemeCard + `</div>`
    + `<div class="chart-grid cols2">`
      + dupCard(pr.doppelteUrl,'Doppelte URLs nach Quellen','Gleiche URL bei mehreren Datensätzen.')
      + dupCard(pr.doppelteTitel,'Doppelte Titel nach Quellen','Gleicher Name bei mehreren Datensätzen.')
    + `</div>`
    + head('🔒 Inhaltstypen & Feld-Füllstände (Team)','Mis-Tagging-Prüfung und Vollständigkeit')
    + `<div class="chart-grid cols3">`
      + lrtCard
      + fuellbar('Metadatenfelder (je Quelldatensatz)', ff.metadaten, ff.metadatenBasis||0, '#2e6ca8')
      + fuellbar('KI-/Rechtshinweise (je Crawler-Profil)', ff.ki, ff.kiBasis||0, '#a85b00')
    + `</div>`
    + head('🔒 Kuration & Marker (Team)','Korrekturliste und Provenienz-Marker')
    + `<div class="chart-grid cols2">` + korrekturCard + provCard + `</div>`
    + head('🔒 Informationsherkunft (Team)','welches Feld kommt aus welcher Quelle')
    + `<div class="chart-grid cols3">`
      + (d.feldHerkunft||[]).map(src=>{ const max=Math.max(1,...src.felder.map(f=>f.anzahl));
        return `<div class="chart-card"><h3>${esc(src.quelle)}</h3><p class="hint">${num(src.gesamt)} Feldwerte aus dieser Quelle</p><div class="barlist">${src.felder.map(f=>`<div class="barrow"><span class="bl" title="${esc(f.feld)}">${esc(f.feld)}</span><span class="bar" style="width:${Math.round(f.anzahl/max*100)}%;background:#2e6ca8"></span><span class="bv">${num(f.anzahl)}</span></div>`).join('')}</div></div>`; }).join('')
    + `</div>`;
  $('#view-stats').insertAdjacentHTML('beforeend', html);
}
