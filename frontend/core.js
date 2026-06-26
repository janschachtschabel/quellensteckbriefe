'use strict';
// core.js — DOM helpers, state, API client, toast (foundation for all other scripts).

const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const state = { page: 1, team: false, view: 'list', sel: new Set(), charts: [] };

const esc = (s) => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
// Only allow http(s) links — blocks javascript:/data:/etc. schemes if they ever land in data.
const safeUrl = (u) => /^https?:\/\//i.test(String(u ?? '')) ? String(u) : '';
const arr = (v) => Array.isArray(v) ? v : (v ? [v] : []);
const num = (n) => (n || 0).toLocaleString('de');
const headers = () => ({});   // team auth rides on the httpOnly session cookie (auto-sent)

async function api(path){ const r = await fetch(path, {headers: headers()}); if(!r.ok) throw new Error(r.status); return r.json(); }
async function apiPost(path, body){ const r = await fetch(path, {method:'POST', headers:{'Content-Type':'application/json',...headers()}, body:JSON.stringify(body)}); if(!r.ok) throw new Error(r.status); return r.json(); }
function toast(msg){ const t=$('#toast'); t.textContent=msg; t.classList.remove('hidden'); clearTimeout(t._t); t._t=setTimeout(()=>t.classList.add('hidden'),2600); }
