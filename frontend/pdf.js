'use strict';
// pdf.js — PDF-Erzeugung (jsPDF): Steckbrief-, Tabellen-, Statistik-PDF.

// ---- PDF (jsPDF, WLO-Branding) --------------------------------------------
// PDF-Optionen aus der Auswahl-Leiste (Vorlage / Vorschaubilder / Einzeldateien)
function pdfOpts(){ return {
  template:($('#pdfTemplate')&&$('#pdfTemplate').value)||'standard',
  preview:!!($('#pdfPreview')&&$('#pdfPreview').checked),
  separate:!!($('#pdfSeparate')&&$('#pdfSeparate').checked) }; }
const sleep=(ms)=>new Promise(r=>setTimeout(r,ms));
// Vorschaubild über den Server-Proxy als DataURL holen (CORS-frei für jsPDF)
async function loadThumb(url){
  try{
    const r=await fetch('/api/thumb?url='+encodeURIComponent(url));
    if(!r.ok) return null;
    const blob=await r.blob();
    return await new Promise(res=>{ const fr=new FileReader(); fr.onloadend=()=>res(fr.result); fr.onerror=()=>res(null); fr.readAsDataURL(blob); });
  }catch{ return null; }
}
async function selectionPdf(){
  if(!state.sel.size) return;
  const opts=pdfOpts();
  const wantInternal = $('#pdfInternal').checked && state.pw;
  toast(opts.preview?'PDF wird erzeugt (Vorschaubilder laden) …':'PDF wird erzeugt …');
  const d = await apiPost('/api/sources/batch', {ids:[...state.sel]});
  if(opts.separate && d.items.length>1){
    for(const it of d.items){ await buildPdf([it], wantInternal, {...opts, quiet:true}); await sleep(350); }
    toast(`${d.items.length} Einzel-PDFs erzeugt.`);
  } else {
    await buildPdf(d.items, wantInternal, opts);
  }
}
let _logoPng;
async function loadLogoPng(){
  if(_logoPng!==undefined) return _logoPng;
  try{
    const svg=await (await fetch('/wissenlebtonline_claim.svg')).text();
    _logoPng=await new Promise(res=>{
      const img=new Image();
      img.onload=()=>{ const s=4,c=document.createElement('canvas'); c.width=241*s; c.height=40*s;
        const x=c.getContext('2d'); x.fillStyle='#fff'; x.fillRect(0,0,c.width,c.height); x.drawImage(img,0,0,c.width,c.height);
        res(c.toDataURL('image/png')); };
      img.onerror=()=>res('');
      img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(svg);
    });
  }catch{ _logoPng=''; }
  return _logoPng;
}
async function buildPdf(records, internal, opts){
  if(!window.jspdf){ toast('PDF-Bibliothek lädt noch – bitte erneut versuchen.'); return; }
  opts = opts || {};
  const isCompact = opts.template === 'compact';
  const wantPrev = !!opts.preview;
  const { jsPDF } = window.jspdf;
  const logoPng = await loadLogoPng();
  const stand = state.dataStand || '';
  const doc = new jsPDF({orientation:'portrait', unit:'mm', format:'a4'});
  const P=[0,59,124], MUT=[91,107,134], TXT=[40,50,70];
  const W=doc.internal.pageSize.getWidth(), H=doc.internal.pageSize.getHeight(), M=14, CW=W-2*M;
  let page=0;
  // Balken in WissenLebtOnline-Farben: Blau → Hellblau → Slate → Lime → Pink
  const BAR=[[0,59,124],[46,108,168],[123,160,201],[163,206,60],[236,74,112]];
  const drawHeader=()=>{
    const sw=W/BAR.length; BAR.forEach((c,i)=>{doc.setFillColor(...c);doc.rect(i*sw,0,sw+1,7,'F');});
    if(logoPng){ try{ doc.addImage(logoPng,'PNG', W-M-46, 9.4, 46, 7.6); }catch(e){} }
    else { doc.setFontSize(12);doc.setFont('helvetica','bold');doc.setTextColor(...P);doc.text('WissenLebt',W-52,15);
      const w=doc.getTextWidth('WissenLebt');doc.setTextColor(236,74,112);doc.text('Online',W-52+w+1,15); }
    doc.setFontSize(8);doc.setTextColor(...MUT);doc.setFont('helvetica','normal');doc.text(`Quellensteckbrief · Seite ${page}`,M,15);
  };
  const drawFooter=()=>{
    doc.setDrawColor(...MUT);doc.setLineWidth(.3);doc.line(M,H-16,W-M,H-16);
    doc.setFontSize(6.5);doc.setTextColor(...MUT);
    doc.text('Gefördert vom Bundesministerium für Bildung und Forschung · Finanziert von der Europäischen Union',M,H-11);
    doc.text(new Date().toLocaleDateString('de-DE'),W-M-22,H-11);
  };
  const section=(title,y)=>{doc.setFillColor(0,59,124);doc.rect(M,y,CW,6.5,'F');doc.setFontSize(9);doc.setTextColor(255,255,255);doc.setFont('helvetica','bold');doc.text(title,M+2,y+4.6);return y+8.5;};
  const table=(y,body,head)=>{ doc.autoTable({startY:y, head:head, body:body, theme:head?'grid':'plain',
      headStyles:{fillColor:[0,59,124],textColor:[255,255,255],fontSize:7},
      styles:{fontSize:head?6.5:8,cellPadding:head?1.4:2,overflow:'linebreak'},
      columnStyles:head?{0:{cellWidth:34},1:{cellWidth:'auto'},2:{cellWidth:'auto'},3:{cellWidth:42}}:{0:{fontStyle:'bold',cellWidth:46,textColor:MUT},1:{cellWidth:'auto',textColor:TXT}},
      alternateRowStyles:{fillColor:[248,250,252]}, rowPageBreak:'avoid', margin:{left:M,right:M}});
    return doc.lastAutoTable.finalY+4; };
  const pb=(y)=>{ if(y>H-46){drawFooter();doc.addPage();page++;drawHeader();return 24;} return y; };
  const clip=(v,n)=>{ v=String(v||'').replace(/\s+/g,' ').trim(); return v.length>n?v.slice(0,n)+'…':v; };
  // KI-Werte: moderat kürzen; sehr lange (z.B. ganze robots.txt) ganz weglassen
  const clipKi=(v)=>{ v=String(v||'').replace(/\s+/g,' ').trim(); return v.length>400?'':(v.length>200?v.slice(0,200)+'…':v); };

  // Vorschaubilder vorab über den Server-Proxy laden (CORS-frei für jsPDF)
  const prevImgs = {};
  if(wantPrev){
    await Promise.all(records.map(async r=>{
      if(r.previewUrl){ const b=await loadThumb(r.previewUrl); if(b) prevImgs[r.id]=b; }
    }));
  }

  records.forEach((r,idx)=>{
    if(idx>0) doc.addPage(); page++; drawHeader();
    const p=r.public, id=r.identity;
    // Kopf: Vorschaubild links (Seitenverhältnis erhalten), Titel/Meta/Beschreibung rechts.
    // Feste Spaltenbreite (slotW), Höhe dynamisch aus den echten Bildmaßen; sehr hohe
    // Bilder werden über maxH per fit-by-height begrenzt (nie verzerrt, nur skaliert).
    const img=prevImgs[r.id], slotW=38, maxH=34, topY=22;
    let dw=0, dh=0;
    if(img){
      let ratio=0.72, fmt='JPEG';
      try{ const pr=doc.getImageProperties(img); if(pr){ if(pr.width&&pr.height) ratio=pr.height/pr.width; if(pr.fileType) fmt=pr.fileType; } }catch(e){}
      dw=slotW; dh=dw*ratio;
      if(dh>maxH){ dh=maxH; dw=dh/ratio; }
      try{ doc.addImage(img,fmt,M,topY,dw,dh); }
      catch(e){ try{ doc.addImage(img,M,topY,dw,dh); }catch(_){ dw=dh=0; } }
    }
    const tx = img ? M+slotW+5 : M, tw = img ? CW-slotW-5 : CW;
    doc.setFontSize(15);doc.setFont('helvetica','bold');doc.setTextColor(...P);
    const tl=doc.splitTextToSize(r.name||'-',tw); tl.slice(0,3).forEach((ln,i)=>doc.text(ln,tx,topY+5+i*6));
    let ty=topY+5+Math.min(3,tl.length)*6+1;
    doc.setFontSize(8.5);doc.setFont('helvetica','normal');doc.setTextColor(...MUT);
    doc.text(`${r.kind} · ${num(r.contentCount)} Inhalte · ${r.erschliessung||''}`,tx,ty); ty+=5;
    if(p.Beschreibung){ doc.setTextColor(...TXT);const dl=doc.splitTextToSize(p.Beschreibung,tw); dl.slice(0,img?3:4).forEach((ln,i)=>doc.text(ln,tx,ty+i*4)); ty+=Math.min(img?3:4,dl.length)*4; }
    let y=Math.max(ty, topY+dh)+4;

    y=section('Allgemeine Informationen',y);
    y=table(y,[['Bezugsquelle',id.bezugsquelle||'-'],['URL',p.URL||'-'],['Inhaltsanzahl',num(r.contentCount)+(stand?` (Datenstand: ${stand})`:'')],['Quelldatensatz (Node-ID)',id.nodeId||'-'],['Crawler/Spider',id.spider||'-']]);

    y=section('Lizenz',y);
    y=table(y,[['Lizenz',p.Lizenz||'-'],['OER',p.OER?'ja':'-'],['Urheber',clip(p.Urheber,150)||'-']]);

    const arrj=(x)=>Array.isArray(x)?x.join(', '):(x||'');
    const bRows=[['Fächer',(p.Faecher||[]).join(', ')||'-'],['Bildungsstufen',(p.Bildungsstufen||[]).join(', ')||'-'],
      ['Inhaltstypen',(p.Inhaltstypen||[]).join(', ')||'-'],['Zielgruppe',arrj(p.Zielgruppe)],['Alter',p.Alter||''],
      ['Sprache',p.Sprache||'-'],['Sprachniveau',arrj(p.Sprachniveau)],['Zielsprache',p.Zielsprache||''],
      ['Lehrplanbezug',clip(arrj(p.Lehrplanbezug),120)],['FSK',p.FSK||''],['Schlagworte',(p.Schlagworte||[]).join(', ')||'-']]
      .filter(rw=>String(rw[1]).trim());
    y=section('Bildung & Einordnung',y);
    y=table(y,bRows);

    // Kompakt-Vorlage: nur Allgemein + Lizenz + Bildung (1 Seite). Standard: alles.
    if(!isCompact){
      const qrows=Object.entries(r.quality||{});
      if(qrows.length){ y=pb(y); y=section('Qualitätsmerkmale (gepflegt)',y); y=table(y, qrows.map(([k,v])=>[k,String(v)])); }

      if(r.fieldGeneration && r.fieldGeneration.length){
        y=pb(y); y=section('Metadaten-Erzeugung (Crawler-Provenienz)',y);
        y=table(y, r.fieldGeneration.map(f=>[f.item,f.field,f.aktiv?'aktiv':f.status,f.how||(f.aktiv?'aus Quelldaten':'')]), [['Item','Feld','Status','Erzeugung']]);
      }
      if(internal && r.internal){
        y=pb(y); y=section('Interne Infos (Team)',y);
        y=table(y, Object.entries(r.internal).map(([k,v])=>[k,String(v??'-')]));
      }
      // KI-Nutzung & Recht zuletzt: lange Werte gekürzt, sehr lange (robots.txt) weggelassen
      const kiRows=[['robots.txt',p['robots.txt']],['TDM-Hinweis (§44b)',p['TDM-Hinweis (§44b)']],['AGB/Nutzung',p['AGB/Nutzungsbedingungen']],['Lizenz-Check',p['Lizenz-Check']],['API-Nutzung',p['API-Nutzungsbedingungen']]]
        .map(([k,v])=>[k,clipKi(v)]).filter(row=>row[1]);
      if(kiRows.length){ y=pb(y); y=section('KI-Nutzung & Recht',y); y=table(y,kiRows); }
    }
    drawFooter();
  });
  const fn = records.length===1 ? `Steckbrief_${(records[0].name||'quelle').replace(/[^\w]+/g,'_').slice(0,40)}.pdf` : `Quellensteckbriefe_${records.length}.pdf`;
  doc.save(fn);
  if(!opts.quiet) toast(`PDF erzeugt (${records.length} ${records.length===1?'Quelle':'Quellen'}).`);
}

const clipS=(v,n)=>{ v=String(v||'').replace(/\s+/g,' ').trim(); return v.length>n?v.slice(0,n)+'…':v; };

// ---- Tabellen-PDF (Quellenübersicht der aktuellen Filter) ------------------
async function tablePdf(){
  if(!window.jspdf){ toast('PDF-Bibliothek lädt noch …'); return; }
  toast('Tabelle wird erzeugt …');
  let rows;
  try{ rows = await api('/api/export.json?'+filterParams().toString()); }
  catch{ toast('Daten konnten nicht geladen werden.'); return; }
  if(!rows.length){ toast('Keine Quellen im aktuellen Filter.'); return; }
  const CAP=1500, capped=rows.length>CAP, totalN=rows.length; if(capped) rows=rows.slice(0,CAP);
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({orientation:'landscape', unit:'mm', format:'a4'});
  const P=[0,59,124], MUT=[91,107,134];
  const KN={crawler:'Crawler',manuell:'manuell',bezugsquelle:'Bezugsquelle'};
  doc.setFontSize(15);doc.setTextColor(...P);doc.setFont('helvetica','bold');
  doc.text('WissenLebtOnline · Quellenübersicht',14,16);
  doc.setFontSize(9);doc.setTextColor(...MUT);doc.setFont('helvetica','normal');
  doc.text(`${num(totalN)} Quellen${capped?` (gekürzt auf ${CAP})`:''}`+(state.dataStand?` · Datenstand: ${state.dataStand}`:'')+` · erstellt ${new Date().toLocaleDateString('de-DE')}`,14,22);
  doc.autoTable({ startY:26,
    head:[['Name','Art','Inhalte','Lizenz','OER','Bildungsstufen','Fächer','Erschließung']],
    body:rows.map(r=>[clipS(r.name,46),KN[r.kind]||r.kind,num(r.contentCount),clipS(r.Lizenz,16),r.OER||'',clipS((r.Bildungsstufen||'').replace(/ \| /g,', '),34),clipS((r.Faecher||'').replace(/ \| /g,', '),34),clipS(r.erschliessung,26)]),
    theme:'striped', headStyles:{fillColor:P,textColor:[255,255,255],fontSize:8},
    styles:{fontSize:7,cellPadding:1.6,overflow:'linebreak'},
    columnStyles:{0:{cellWidth:62},2:{halign:'right',cellWidth:18},4:{halign:'center',cellWidth:12}},
    margin:{left:14,right:14} });
  doc.save('Quellenuebersicht.pdf');
  toast(`Tabelle erzeugt (${num(totalN)} Quellen${capped?`, gekürzt auf ${CAP}`:''}).`);
}

// ---- Statistik-PDF (Verteilungen) -----------------------------------------
async function statsPdf(){
  if(!window.jspdf){ toast('PDF-Bibliothek lädt noch …'); return; }
  let s=state.lastStats;
  if(!s){ try{ s=await api('/api/stats/full'); }catch{ toast('Statistik nicht verfügbar.'); return; } }
  const { jsPDF } = window.jspdf;
  const doc=new jsPDF({orientation:'portrait',unit:'mm',format:'a4'});
  const P=[0,59,124],MUT=[91,107,134]; const W=doc.internal.pageSize.getWidth(),H=doc.internal.pageSize.getHeight(),M=14,CW=W-2*M;
  let y=18;
  doc.setFontSize(16);doc.setTextColor(...P);doc.setFont('helvetica','bold');doc.text('WissenLebtOnline · Quellenstatistik',M,y); y+=6;
  doc.setFontSize(9);doc.setTextColor(...MUT);doc.setFont('helvetica','normal');
  doc.text((s.meta&&s.meta.generatedAt?`Datenstand: ${s.meta.generatedAt} · `:'')+`erstellt ${new Date().toLocaleDateString('de-DE')}`,M,y); y+=6;
  const sec=(t)=>{ if(y>H-30){doc.addPage();y=18;} doc.setFillColor(...P);doc.rect(M,y,CW,6.5,'F');doc.setFontSize(10);doc.setTextColor(255,255,255);doc.setFont('helvetica','bold');doc.text(t,M+2,y+4.6); y+=9; };
  const tbl=(head,body)=>{ doc.autoTable({startY:y,head:head?[head]:undefined,body,theme:head?'striped':'plain',headStyles:{fillColor:P,textColor:[255,255,255],fontSize:8},styles:{fontSize:8,cellPadding:1.8},columnStyles:{1:{halign:'right',cellWidth:30}},margin:{left:M,right:M}}); y=doc.lastAutoTable.finalY+5; };
  const t=s.totals, cc=s.contentCoverage, fg=s.fieldGeneration;
  sec('Zusammenfassung');
  tbl(null,[['Quellen gesamt',num(t.quellenGesamt)],['Inhalte gesamt',num(t.inhalteGesamt)],['Quelldatensätze',num(t.quelldatensaetze)],['Crawler-Quellen',num(t.crawler)],['manuell angelegt',num(t.manuell)],['reine Bezugsquellen',num(t.bezugsquellenOhneQuelle)],['OER',`${num(s.oer.count)} (${s.oer.percent}%)`],['mit Feld-Profil',num(fg.crawlerWithProfile)],['Ø aktive Felder/Crawler',String(fg.avgFieldsPerCrawler)]]);
  sec('Inhaltsabdeckung nach Quellentyp');
  tbl(['Quellentyp','Inhalte'],[['über Bezugsquelle',num(cc.bezugsquelle)],['über Crawler',num(cc.crawler)],['mit Quelldatensatz',num(cc.quelldatensatz)],['gesamt',num(cc.gesamt)]]);
  const dist=(title,items)=>{ if(!items||!items.length)return; sec(title); tbl([title.split(' (')[0],'Anzahl'],items.map(i=>[clipS(i.value,54),num(i.count)])); };
  dist('Art der Quelle',[{value:'Crawler',count:s.byKind.crawler},{value:'manuell',count:s.byKind.manuell},{value:'reine Bezugsquelle',count:s.byKind.bezugsquelle}]);
  dist('Inhaltsmengen je Quelle',s.contentBrackets);
  dist('Top-Quellen nach Inhalten',s.topByContent.slice(0,15).map(c=>({value:c.name,count:c.count})));
  dist('Top-Crawler (Inhalte)',s.topCrawler.slice(0,15).map(c=>({value:c.name,count:c.count})));
  dist('Top-Fächer',s.topSubjects.slice(0,15));
  dist('Lizenz-Verteilung',s.licenseDistribution.slice(0,12));
  dist('Bildungsstufen',s.topLevels.slice(0,12));
  dist('Sprachen',s.topLanguages.slice(0,10));
  dist('Inhaltstypen',s.topLrt.slice(0,12));
  dist('Metadaten-Erzeugung (Methode)',fg.byMethod);
  doc.save('Quellenstatistik.pdf');
  toast('Statistik-PDF erzeugt.');
}
