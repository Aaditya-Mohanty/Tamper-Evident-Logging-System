import hashlib
import json
import os
import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
LOG_FILE = "secure_log.json"

def compute_hash(entry: dict) -> str:
    entry_copy = {k: v for k, v in entry.items() if k != "hash"}
    serialized = json.dumps(entry_copy, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()

def load_log() -> list:
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        return json.load(f)

def save_log(log: list):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=4)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SecureChain — Audit Log System</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:       #050810;
    --bg2:      #080d1a;
    --bg3:      #0c1224;
    --panel:    #0a1020;
    --border:   #1a2a4a;
    --accent:   #00f5c4;
    --accent2:  #0088ff;
    --accent3:  #ff3a6e;
    --warn:     #ffb020;
    --text:     #c8d8f0;
    --muted:    #4a6080;
    --glow:     0 0 20px rgba(0,245,196,0.25);
    --glow2:    0 0 20px rgba(0,136,255,0.25);
  }

  * { margin:0; padding:0; box-sizing:border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Rajdhani', sans-serif;
    font-size: 15px;
    min-height: 100vh;
    overflow-x: hidden;
  }

  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,245,196,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,245,196,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  body::after {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    animation: scan 6s linear infinite;
    z-index: 1;
    pointer-events: none;
  }
  @keyframes scan { 0%{top:0} 100%{top:100vh} }

  .container { max-width: 1280px; margin: 0 auto; padding: 24px; position: relative; z-index: 2; }

  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 28px;
    background: linear-gradient(135deg, var(--bg2), var(--bg3));
    border: 1px solid var(--border);
    border-bottom: 2px solid var(--accent);
    border-radius: 4px 4px 0 0;
    margin-bottom: 2px;
    position: relative;
    overflow: hidden;
  }
  header::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 60%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0,245,196,0.04), transparent);
    animation: shimmer 4s infinite;
  }
  @keyframes shimmer { to { left: 200%; } }

  .logo {
    font-family: 'Orbitron', monospace;
    font-size: 22px;
    font-weight: 900;
    letter-spacing: 3px;
    color: var(--accent);
    text-shadow: var(--glow);
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .logo-icon { font-size: 28px; }
  .logo-sub { font-family: 'Share Tech Mono'; font-size: 11px; color: var(--muted); letter-spacing: 2px; display:block; margin-top:2px; }

  .status-bar { display:flex; gap:20px; align-items:center; }
  .status-dot {
    display: flex; align-items: center; gap: 8px;
    font-family: 'Share Tech Mono'; font-size: 12px; color: var(--muted);
  }
  .dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent);
    animation: pulse 2s infinite;
  }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

  /* Stats row */
  .stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 2px;
    margin-bottom: 2px;
  }
  .stat-card {
    background: var(--panel);
    border: 1px solid var(--border);
    padding: 18px 22px;
    position: relative;
    overflow: hidden;
    transition: all 0.25s;
    cursor: default;
  }
  /* clickable stat cards */
  .stat-card.clickable {
    cursor: pointer;
  }
  .stat-card.clickable:hover {
    border-color: var(--accent);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
  }
  .stat-card.clickable:hover .stat-hint { opacity: 1; }
  .stat-card.active-filter {
    outline: 2px solid var(--muted);
    outline-offset: 2px;
  }
  .stat-card.c1.active-filter { outline-color: var(--accent); }
  .stat-card.c2.active-filter { outline-color: var(--accent2); }
  .stat-card.c3.active-filter { outline-color: var(--accent3); }
  .stat-card.c4.active-filter { outline-color: var(--warn); }

  .stat-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
  }
  .stat-card.c1::after { background: var(--accent); }
  .stat-card.c2::after { background: var(--accent2); }
  .stat-card.c3::after { background: var(--accent3); }
  .stat-card.c4::after { background: var(--warn); }

  .stat-label { font-family:'Share Tech Mono'; font-size:10px; color:var(--muted); letter-spacing:2px; text-transform:uppercase; margin-bottom:8px; }
  .stat-value { font-family:'Orbitron'; font-size:28px; font-weight:700; }
  .stat-value.c1 { color:var(--accent); text-shadow: 0 0 12px rgba(0,245,196,0.4); }
  .stat-value.c2 { color:var(--accent2); text-shadow: 0 0 12px rgba(0,136,255,0.4); }
  .stat-value.c3 { color:var(--accent3); text-shadow: 0 0 12px rgba(255,58,110,0.4); }
  .stat-value.c4 { color:var(--warn); text-shadow: 0 0 12px rgba(255,176,32,0.4); }
  .stat-sub { font-family:'Share Tech Mono'; font-size:10px; color:var(--muted); margin-top:4px; }
  .stat-hint { font-family:'Share Tech Mono'; font-size:9px; color:var(--muted); opacity:0; margin-top:5px; transition:opacity 0.2s; }

  /* Filter banner */
  .filter-banner {
    display: none;
    align-items: center;
    gap: 12px;
    padding: 10px 18px;
    background: var(--bg2);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    margin-bottom: 2px;
    font-family: 'Share Tech Mono';
    font-size: 12px;
    color: var(--accent);
    animation: fadeIn 0.3s ease;
  }
  .filter-banner.visible { display: flex; }
  .filter-banner.c-orange { border-left-color: var(--warn); color: var(--warn); }
  .filter-banner.c-red    { border-left-color: var(--accent3); color: var(--accent3); }
  .filter-banner-clear {
    margin-left: auto;
    background: transparent;
    border: 1px solid var(--border);
    color: var(--muted);
    padding: 4px 12px;
    font-family: 'Share Tech Mono';
    font-size: 11px;
    cursor: pointer;
    border-radius: 2px;
    transition: all 0.2s;
  }
  .filter-banner-clear:hover { border-color: var(--accent3); color: var(--accent3); }

  /* Main grid */
  .main-grid {
    display: grid;
    grid-template-columns: 380px 1fr;
    gap: 2px;
  }

  .panel {
    background: var(--panel);
    border: 1px solid var(--border);
  }
  .panel-header {
    padding: 14px 20px;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
    background: var(--bg2);
  }
  .panel-title {
    font-family: 'Orbitron'; font-size: 11px; font-weight: 700;
    letter-spacing: 3px; text-transform: uppercase; color: var(--accent);
  }
  .panel-body { padding: 20px; }

  .form-group { margin-bottom: 16px; }
  label { display:block; font-family:'Share Tech Mono'; font-size:11px; color:var(--muted); letter-spacing:2px; text-transform:uppercase; margin-bottom:6px; }

  input[type=text], select, textarea {
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 2px;
    color: var(--text);
    font-family: 'Share Tech Mono';
    font-size: 13px;
    padding: 10px 14px;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  input:focus, select:focus, textarea:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 1px rgba(0,245,196,0.2);
  }
  select option { background: var(--bg2); }
  textarea { resize: vertical; min-height: 80px; }

  .btn {
    width: 100%;
    padding: 12px;
    border: none;
    border-radius: 2px;
    font-family: 'Orbitron';
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
  }
  .btn-primary {
    background: linear-gradient(135deg, #00c99e, #00f5c4);
    color: #050810;
  }
  .btn-primary:hover { box-shadow: 0 0 20px rgba(0,245,196,0.5); transform: translateY(-1px); }
  .btn-primary:active { transform: translateY(0) scale(0.98); }

  .btn-verify {
    background: linear-gradient(135deg, #005bcc, #0088ff);
    color: #fff;
    margin-top: 10px;
  }
  .btn-verify:hover { box-shadow: 0 0 20px rgba(0,136,255,0.5); transform: translateY(-1px); }
  .btn-verify:active { transform: translateY(0) scale(0.98); }

  .btn-tamper {
    background: transparent;
    border: 1px solid var(--accent3);
    color: var(--accent3);
    margin-top: 10px;
    font-size: 11px;
  }
  .btn-tamper:hover { background: rgba(255,58,110,0.1); box-shadow: 0 0 14px rgba(255,58,110,0.3); }
  .btn-tamper:active { transform: scale(0.98); }

  /* Log feed */
  .log-feed { max-height: 560px; overflow-y: auto; }
  .log-feed::-webkit-scrollbar { width: 4px; }
  .log-feed::-webkit-scrollbar-track { background: var(--bg); }
  .log-feed::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

  .log-entry {
    padding: 14px 16px;
    border-left: 3px solid var(--border);
    margin-bottom: 6px;
    background: var(--bg2);
    border-radius: 0 2px 2px 0;
    transition: all 0.3s;
    animation: slideIn 0.4s ease;
    cursor: default;
  }
  @keyframes slideIn { from { opacity:0; transform:translateX(-10px); } to { opacity:1; transform:translateX(0); } }
  @keyframes fadeIn  { from { opacity:0; } to { opacity:1; } }

  .log-entry:hover { border-left-color: var(--accent); background: var(--bg3); }
  .log-entry.tampered { border-left-color: var(--accent3) !important; background: rgba(255,58,110,0.06); }
  .log-entry.ok { border-left-color: var(--accent); }
  .log-entry.highlight-flash { animation: flashEntry 0.6s ease; }
  @keyframes flashEntry { 0%,100%{background:var(--bg2)} 50%{background:rgba(0,245,196,0.08)} }

  .log-meta { display:flex; align-items:center; gap:10px; margin-bottom:6px; }
  .log-id { font-family:'Orbitron'; font-size:10px; color:var(--muted); }
  .badge {
    font-family:'Share Tech Mono'; font-size:10px; padding:2px 8px;
    border-radius:2px; letter-spacing:1px; text-transform:uppercase;
  }
  .badge-login    { background:rgba(0,136,255,0.15); color:var(--accent2); border:1px solid rgba(0,136,255,0.3); }
  .badge-tx       { background:rgba(0,245,196,0.10); color:var(--accent);  border:1px solid rgba(0,245,196,0.2); }
  .badge-logout   { background:rgba(255,176,32,0.10); color:var(--warn);   border:1px solid rgba(255,176,32,0.2); }
  .badge-error    { background:rgba(255,58,110,0.10); color:var(--accent3); border:1px solid rgba(255,58,110,0.2); }
  .badge-other    { background:rgba(200,216,240,0.05); color:var(--muted); border:1px solid var(--border); }

  .log-desc { font-size:14px; color:var(--text); margin-bottom:6px; font-weight:500; }
  .log-hash { font-family:'Share Tech Mono'; font-size:10px; color:var(--muted); word-break:break-all; }
  .log-time { font-family:'Share Tech Mono'; font-size:10px; color:var(--muted); margin-left:auto; }

  .verify-result {
    padding: 16px;
    border-radius: 2px;
    margin-top: 16px;
    font-family: 'Share Tech Mono';
    font-size: 12px;
    display: none;
    animation: fadeIn 0.3s ease;
  }
  .verify-ok    { background:rgba(0,245,196,0.06); border:1px solid rgba(0,245,196,0.3); color:var(--accent); }
  .verify-fail  { background:rgba(255,58,110,0.06); border:1px solid rgba(255,58,110,0.3); color:var(--accent3); }
  .verify-line  { margin-bottom:4px; }

  .toast {
    position: fixed; bottom: 30px; right: 30px;
    padding: 14px 20px;
    background: var(--bg3);
    border: 1px solid var(--accent);
    color: var(--accent);
    font-family: 'Share Tech Mono';
    font-size: 12px;
    border-radius: 2px;
    box-shadow: var(--glow);
    z-index: 999;
    transform: translateY(80px);
    opacity: 0;
    transition: all 0.3s;
  }
  .toast.show { transform: translateY(0); opacity: 1; }
  .toast.error { border-color: var(--accent3); color: var(--accent3); box-shadow: 0 0 20px rgba(255,58,110,0.3); }

  .chain-mini { display:flex; align-items:center; gap:4px; padding:12px 16px; background:var(--bg); border-top:1px solid var(--border); flex-wrap:wrap; }
  .chain-node {
    width:10px; height:10px; border-radius:50%;
    background: var(--accent);
    box-shadow: 0 0 6px rgba(0,245,196,0.6);
    flex-shrink:0;
    transition: all 0.3s;
    cursor: pointer;
  }
  .chain-node:hover { transform: scale(1.4); }
  .chain-node.tampered-node { background:var(--accent3); box-shadow:0 0 6px rgba(255,58,110,0.6); }
  .chain-link { width:16px; height:1px; background:var(--border); flex-shrink:0; }

  .empty-state { text-align:center; padding:60px 20px; color:var(--muted); font-family:'Share Tech Mono'; font-size:12px; }
  .empty-icon  { font-size:40px; margin-bottom:12px; opacity:0.3; }

  .divider { height:1px; background:var(--border); margin:16px 0; }

  @media(max-width:900px) {
    .main-grid { grid-template-columns: 1fr; }
    .stats-row { grid-template-columns: repeat(2,1fr); }
  }
</style>
</head>
<body>
<div class="container">

  <header>
    <div class="logo">
      <span class="logo-icon">⛓</span>
      <div>
      Tamper Evident Logging
        <span class="logo-sub">TAMPER-EVIDENT AUDIT LOG v1.0</span>
      </div>
    </div>
    <div class="status-bar">
      <div class="status-dot"><span class="dot"></span>SYSTEM ACTIVE</div>
      <div class="status-dot" id="clock" style="color:var(--text)"></div>
    </div>
  </header>

  <div class="stats-row">
    <div class="stat-card c1 clickable" id="sc-total" onclick="statCardClick('total')" title="Click to show all entries">
      <div class="stat-label">Total Entries</div>
      <div class="stat-value c1" id="s-total">0</div>
      <div class="stat-sub">in chain</div>
      <div class="stat-hint">↑ show all entries</div>
    </div>
    <div class="stat-card c2 clickable" id="sc-status" onclick="statCardClick('status')" title="Click to run chain verification">
      <div class="stat-label">Chain Status</div>
      <div class="stat-value c2" id="s-status" style="font-size:18px;padding-top:6px">UNVERIFIED</div>
      <div class="stat-sub">run verify to check</div>
      <div class="stat-hint">↑ click to verify now</div>
    </div>
    <div class="stat-card c3 clickable" id="sc-violations" onclick="statCardClick('violations')" title="Click to show tampered entries">
      <div class="stat-label">Violations</div>
      <div class="stat-value c3" id="s-violations">0</div>
      <div class="stat-sub">tampering detected</div>
      <div class="stat-hint">↑ show tampered entries</div>
    </div>
    <div class="stat-card c4 clickable" id="sc-last" onclick="statCardClick('last')" title="Click to jump to latest entry">
      <div class="stat-label">Last Entry</div>
      <div class="stat-value c4" style="font-size:14px;padding-top:8px" id="s-last">—</div>
      <div class="stat-sub">timestamp</div>
      <div class="stat-hint">↑ jump to latest</div>
    </div>
  </div>

  <!-- Filter banner -->
  <div class="filter-banner" id="filter-banner">
    <span id="filter-banner-text">🔍 Filtering...</span>
    <button class="filter-banner-clear" onclick="clearStatFilter()">✕ Clear Filter</button>
  </div>

  <div class="main-grid">

    <!-- LEFT: Controls -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">⊕ Add Log Entry</span>
      </div>
      <div class="panel-body">
        <div class="form-group">
          <label>Event Type</label>
          <select id="f-type">
            <option value="LOGIN">LOGIN</option>
            <option value="LOGOUT">LOGOUT</option>
            <option value="TRANSACTION">TRANSACTION</option>
            <option value="ERROR">ERROR</option>
            <option value="ACCESS">ACCESS</option>
            <option value="MODIFY">MODIFY</option>
          </select>
        </div>
        <div class="form-group">
          <label>Username</label>
          <input type="text" id="f-user" placeholder="e.g. admin" />
        </div>
        <div class="form-group">
          <label>Description</label>
          <textarea id="f-desc" placeholder="Describe the event..."></textarea>
        </div>
        <button class="btn btn-primary" onclick="addEntry()">⊕ COMMIT ENTRY</button>
        <div class="divider"></div>
        <button class="btn btn-verify" onclick="verifyChain()">◈ VERIFY CHAIN INTEGRITY</button>
        <button class="btn btn-tamper" onclick="simulateTamper()">⚡ SIMULATE TAMPER ATTACK</button>

        <div class="verify-result" id="verify-box"></div>
      </div>
    </div>

    <!-- RIGHT: Log Feed -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">◎ Live Audit Chain</span>
        <span style="font-family:'Share Tech Mono';font-size:10px;color:var(--muted)" id="entry-count">0 ENTRIES</span>
      </div>
      <div class="chain-mini" id="chain-vis"></div>
      <div class="log-feed panel-body" id="log-feed">
        <div class="empty-state">
          <div class="empty-icon">⛓</div>
          No log entries yet.<br>Add your first entry to begin the chain.
        </div>
      </div>
    </div>

  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const API = '';
let violations = 0;
let allLogs = [];
let tamperedIds = [];
let activeStatFilter = null;

function showToast(msg, err=false) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast show' + (err ? ' error' : '');
  setTimeout(() => t.className = 'toast', 3000);
}

function clock() {
  document.getElementById('clock').textContent = new Date().toISOString().replace('T',' ').slice(0,19) + ' UTC';
}
setInterval(clock, 1000); clock();

function getBadge(type) {
  const map = { LOGIN:'badge-login', LOGOUT:'badge-logout', TRANSACTION:'badge-tx', ERROR:'badge-error' };
  const cls = map[type] || 'badge-other';
  return `<span class="badge ${cls}">${type}</span>`;
}

// ── STAT CARD CLICK HANDLER ──
function statCardClick(which) {
  if (activeStatFilter === which) {
    clearStatFilter();
    return;
  }

  // special action: status card triggers verify
  if (which === 'status') {
    clearStatFilter();
    verifyChain();
    return;
  }

  // special action: last card scrolls to newest entry
  if (which === 'last') {
    clearStatFilter();
    if (!allLogs.length) { showToast('No entries yet.', true); return; }
    renderFeed(allLogs, tamperedIds);
    setTimeout(() => {
      const feed = document.getElementById('log-feed');
      const first = feed.querySelector('.log-entry');
      if (first) {
        feed.scrollTop = 0;
        first.classList.add('highlight-flash');
        setTimeout(() => first.classList.remove('highlight-flash'), 700);
      }
    }, 50);
    showToast('Jumped to latest entry.');
    return;
  }

  // filter: total = all entries (just clear)
  if (which === 'total') {
    clearStatFilter();
    showToast('Showing all ' + allLogs.length + ' entries.');
    return;
  }

  // filter: violations = show tampered only
  if (which === 'violations') {
    if (!tamperedIds.length) {
      if (allLogs.length === 0) {
        showToast('No entries in chain yet.', true);
      } else {
        showToast('No violations detected. Run Verify first.', true);
      }
      return;
    }
    activeStatFilter = 'violations';
    document.getElementById('sc-violations').classList.add('active-filter');
    const banner = document.getElementById('filter-banner');
    banner.className = 'filter-banner visible c-red';
    document.getElementById('filter-banner-text').textContent = '⚠ Showing tampered / violated entries only — ' + tamperedIds.length + ' found';
    renderFeed(allLogs.filter(e => tamperedIds.includes(e.id)), tamperedIds);
    showToast('Filtered to ' + tamperedIds.length + ' tampered entry/entries.', true);
  }
}

function clearStatFilter() {
  activeStatFilter = null;
  ['sc-total','sc-status','sc-violations','sc-last'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.remove('active-filter');
  });
  document.getElementById('filter-banner').className = 'filter-banner';
  renderFeed(allLogs, tamperedIds);
}

// ── RENDER HELPERS ──
function renderFeed(logs, tIds) {
  const feed = document.getElementById('log-feed');
  if (!logs.length) {
    feed.innerHTML = '<div class="empty-state"><div class="empty-icon">⛓</div>No entries match this filter.</div>';
    return;
  }
  feed.innerHTML = [...logs].reverse().map(e => {
    const isTampered = tIds.includes(e.id);
    return `<div class="log-entry ${isTampered?'tampered':'ok'}" id="entry-${e.id}">
      <div class="log-meta">
        <span class="log-id">#${String(e.id).padStart(4,'0')}</span>
        ${getBadge(e.event_type)}
        <span style="font-family:'Share Tech Mono';font-size:10px;color:var(--muted)">${e.user}</span>
        <span class="log-time">${e.timestamp.slice(0,19).replace('T',' ')}</span>
        ${isTampered ? '<span class="badge badge-error" style="margin-left:4px">⚠ TAMPERED</span>' : ''}
      </div>
      <div class="log-desc">${e.description}</div>
      <div class="log-hash">SHA256: ${e.hash}</div>
    </div>`;
  }).join('');
}

function renderLogs(logs, tIds=[]) {
  allLogs = logs;
  tamperedIds = tIds;

  document.getElementById('s-total').textContent = logs.length;
  document.getElementById('entry-count').textContent = logs.length + ' ENTRIES';

  if (logs.length === 0) {
    document.getElementById('log-feed').innerHTML = '<div class="empty-state"><div class="empty-icon">⛓</div>No log entries yet.<br>Add your first entry to begin the chain.</div>';
    document.getElementById('chain-vis').innerHTML = '';
    return;
  }

  document.getElementById('s-last').textContent = logs[logs.length-1].timestamp.slice(11,19);

  // chain vis — nodes are clickable to scroll to that entry
  document.getElementById('chain-vis').innerHTML = logs.map((e,i) => {
    const isTampered = tIds.includes(e.id);
    return (i > 0 ? '<div class="chain-link"></div>' : '') +
      `<div class="chain-node ${isTampered?'tampered-node':''}" onclick="scrollToEntry(${e.id})" title="Jump to Entry #${e.id}"></div>`;
  }).join('');

  if (activeStatFilter === 'violations') {
    renderFeed(logs.filter(e => tIds.includes(e.id)), tIds);
  } else {
    renderFeed(logs, tIds);
  }
}

function scrollToEntry(id) {
  const feed = document.getElementById('log-feed');
  // entries are rendered in reverse, so entry #id is toward the bottom of the DOM
  const target = document.getElementById('entry-' + id);
  if (target) {
    target.scrollIntoView({ behavior: 'smooth', block: 'center' });
    target.classList.add('highlight-flash');
    setTimeout(() => target.classList.remove('highlight-flash'), 700);
  }
}

async function loadLogs() {
  const r = await fetch('/api/logs');
  const data = await r.json();
  renderLogs(data.logs, tamperedIds);
}

async function addEntry() {
  const type = document.getElementById('f-type').value;
  const user = document.getElementById('f-user').value.trim() || 'anonymous';
  const desc = document.getElementById('f-desc').value.trim();
  if (!desc) { showToast('Description is required.', true); return; }

  const r = await fetch('/api/add', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({event_type:type, user, description:desc})
  });
  const data = await r.json();
  showToast('Entry #' + data.id + ' committed to chain.');
  document.getElementById('f-desc').value = '';
  tamperedIds = [];
  clearStatFilter();
  loadLogs();
  document.getElementById('verify-box').style.display = 'none';
  document.getElementById('s-status').textContent = 'UNVERIFIED';
  document.getElementById('s-status').style.color = 'var(--warn)';
}

async function verifyChain() {
  const r = await fetch('/api/verify');
  const data = await r.json();
  const box = document.getElementById('verify-box');
  box.style.display = 'block';
  violations = data.violations.length;
  tamperedIds = data.tampered_ids;
  document.getElementById('s-violations').textContent = violations;

  if (data.ok) {
    box.className = 'verify-result verify-ok';
    box.innerHTML = `<div class="verify-line">✓ CHAIN VERIFIED — ${data.total} entries checked</div><div class="verify-line">◈ No tampering detected</div><div class="verify-line">◈ All hashes valid</div>`;
    document.getElementById('s-status').textContent = 'VERIFIED';
    document.getElementById('s-status').style.color = 'var(--accent)';
    showToast('Chain integrity confirmed.');
    renderLogs(data.logs, []);
  } else {
    box.className = 'verify-result verify-fail';
    const msgs = data.violations.map(v => `<div class="verify-line">⚠ ${v}</div>`).join('');
    box.innerHTML = `<div class="verify-line">✗ TAMPERING DETECTED — ${violations} violation(s)</div>${msgs}`;
    document.getElementById('s-status').textContent = 'COMPROMISED';
    document.getElementById('s-status').style.color = 'var(--accent3)';
    showToast('⚠ Tampering detected!', true);
    renderLogs(data.logs, data.tampered_ids);
  }
}

async function simulateTamper() {
  if (!confirm('This will corrupt an entry to demo tamper detection. Continue?')) return;
  const r = await fetch('/api/tamper', {method:'POST'});
  const data = await r.json();
  showToast(data.message, true);
  tamperedIds = [];
  clearStatFilter();
  loadLogs();
  document.getElementById('s-status').textContent = 'UNVERIFIED';
  document.getElementById('s-status').style.color = 'var(--warn)';
  document.getElementById('verify-box').style.display = 'none';
}

loadLogs();
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/logs")
def api_logs():
    return jsonify({"logs": load_log()})

@app.route("/api/add", methods=["POST"])
def api_add():
    data = request.json
    log = load_log()
    prev_hash = log[-1]["hash"] if log else "0" * 64
    entry = {
        "id": len(log) + 1,
        "timestamp": datetime.now().isoformat(),
        "event_type": data.get("event_type", "INFO"),
        "description": data.get("description", ""),
        "user": data.get("user", "system"),
        "prev_hash": prev_hash,
    }
    entry["hash"] = compute_hash(entry)
    log.append(entry)
    save_log(log)
    return jsonify({"id": entry["id"]})

@app.route("/api/verify")
def api_verify():
    log = load_log()
    violations = []
    tampered_ids = []
    prev_hash = "0" * 64
    for entry in log:
        expected = compute_hash(entry)
        if entry["hash"] != expected:
            violations.append(f"Entry #{entry['id']} hash mismatch (content modified)")
            tampered_ids.append(entry["id"])
        if entry["prev_hash"] != prev_hash:
            violations.append(f"Entry #{entry['id']} chain break (entry deleted or reordered)")
            if entry["id"] not in tampered_ids:
                tampered_ids.append(entry["id"])
        prev_hash = entry["hash"]
    return jsonify({"ok": len(violations) == 0, "violations": violations, "tampered_ids": tampered_ids, "total": len(log), "logs": log})

@app.route("/api/tamper", methods=["POST"])
def api_tamper():
    log = load_log()
    if not log:
        return jsonify({"message": "No entries to tamper with."})
    log[0]["description"] = "*** TAMPERED BY ATTACKER ***"
    save_log(log)
    return jsonify({"message": "Entry #1 has been corrupted. Run Verify to detect."})

if __name__ == "__main__":
    print("\n  ⛓  SecureChain Audit Log")
    print("  → Open http://localhost:5001\n")
    app.run(debug=False, port=5001)
