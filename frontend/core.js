'use strict';
// core.js — DOM-Helfer, State, API-Client, Toast (Basis fuer alle anderen Skripte).

const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const state = { page: 1, pw: sessionStorage.getItem('qe_pw') || '', view: 'list', sel: new Set(), charts: [] };

const esc = (s) => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const arr = (v) => Array.isArray(v) ? v : (v ? [v] : []);
const num = (n) => (n || 0).toLocaleString('de');
const headers = () => state.pw ? {'X-Team-Password': state.pw} : {};

async function api(path){ const r = await fetch(path, {headers: headers()}); if(!r.ok) throw new Error(r.status); return r.json(); }
async function apiPost(path, body){ const r = await fetch(path, {method:'POST', headers:{'Content-Type':'application/json',...headers()}, body:JSON.stringify(body)}); if(!r.ok) throw new Error(r.status); return r.json(); }
function toast(msg){ const t=$('#toast'); t.textContent=msg; t.classList.remove('hidden'); clearTimeout(t._t); t._t=setTimeout(()=>t.classList.add('hidden'),2600); }
