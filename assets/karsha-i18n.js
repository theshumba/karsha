/* Karsha language layer: English and Hindi on every page, with a toggle.
   Strings live in assets/hi.json: { "s": {english: hindi}, "r": [[regex, replacement], ...] }.
   Text that has no entry stays in English. Choice is remembered in localStorage. */
(function () {
  var KEY = 'karsha.lang', D = document, lang = 'en', dict = null, ready = false, queue = [];
  try { var saved = localStorage.getItem(KEY); lang = saved || ((navigator.language || '').toLowerCase().indexOf('hi') === 0 ? 'hi' : 'en'); } catch (e) {}
  var base = (function () { var s = D.currentScript; return s ? s.src.replace(/karsha-i18n\.js.*$/, '') : '/assets/'; })();
  var ATTRS = ['placeholder', 'aria-label', 'title'];
  var SKIP = /^(SCRIPT|STYLE|TEXTAREA|NOSCRIPT|CODE)$/;

  function tr(text) {
    var t = text.replace(/\s+/g, ' ').trim(); if (!t || !dict) return null;
    var lead = text.match(/^\s*/)[0], trail = text.match(/\s*$/)[0], out = dict.s[t];
    if (out === undefined) {
      for (var i = 0; i < dict.rx.length; i++) { var m = dict.rx[i][0].exec(t); if (m) { out = t.replace(dict.rx[i][0], dict.rx[i][1]); break; } }
    }
    return out === undefined ? null : lead + out + trail;
  }
  function skipEl(el) { return !el || SKIP.test(el.tagName) || (el.closest && el.closest('[data-noi18n]')); }

  function doText(n) {
    var cur = n.nodeValue, src = (n.__hi !== undefined && cur === n.__hi) ? n.__en : cur;
    if (lang === 'hi') {
      var r = tr(src);
      if (r !== null) { n.__en = src; n.__hi = r; if (cur !== r) n.nodeValue = r; }
      else if (n.__hi !== undefined && cur === n.__hi) { n.nodeValue = n.__en; n.__hi = undefined; }
    } else if (n.__hi !== undefined && cur === n.__hi) { n.nodeValue = n.__en; n.__hi = undefined; }
  }
  function doAttrs(el) {
    for (var i = 0; i < ATTRS.length; i++) {
      var a = ATTRS[i]; if (!el.hasAttribute || !el.hasAttribute(a)) continue;
      var k = '__a_' + a, cur = el.getAttribute(a), rec = el[k], src = (rec && cur === rec.hi) ? rec.en : cur;
      if (lang === 'hi') { var r = tr(src); if (r !== null) { el[k] = {en: src, hi: r}; if (cur !== r) el.setAttribute(a, r); } }
      else if (rec && cur === rec.hi) { el.setAttribute(a, rec.en); el[k] = null; }
    }
  }
  function walk(root) {
    if (!root) return;
    if (root.nodeType === 3) { if (!skipEl(root.parentElement)) doText(root); return; }
    if (root.nodeType !== 1 || skipEl(root)) return;
    doAttrs(root);
    var w = D.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT, null), n;
    while ((n = w.nextNode())) {
      if (n.nodeType === 3) { if (!skipEl(n.parentElement)) doText(n); }
      else if (n.nodeType === 1) { if (SKIP.test(n.tagName) || n.hasAttribute('data-noi18n')) { var nx = n; } else doAttrs(n); }
    }
  }
  function title() {
    if (!D.__enTitle) D.__enTitle = D.title;
    if (lang === 'hi') { var r = tr(D.__enTitle); D.title = r !== null ? r : D.__enTitle; } else D.title = D.__enTitle;
  }
  function all() { if (!ready) return; walk(D.body); title(); }

  var pend = false, nodes = [];
  function flush() { pend = false; var l = nodes; nodes = []; for (var i = 0; i < l.length; i++) { if (l[i].isConnected !== false) walk(l[i]); } }
  var mo = new MutationObserver(function (ms) {
    if (!ready) return;
    for (var i = 0; i < ms.length; i++) {
      var m = ms[i];
      if (m.type === 'characterData') nodes.push(m.target);
      else if (m.type === 'attributes') nodes.push(m.target);
      else for (var j = 0; j < m.addedNodes.length; j++) nodes.push(m.addedNodes[j]);
    }
    if (!pend && nodes.length) { pend = true; requestAnimationFrame(flush); }
  });

  function font() {
    if (D.getElementById('kr-font')) return;
    var l = D.createElement('link'); l.id = 'kr-font'; l.rel = 'stylesheet';
    l.href = 'https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap'; D.head.appendChild(l);
  }
  function paintToggle() {
    var t = D.querySelector('.kr-lang'); if (!t) return;
    t.querySelectorAll('button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.l === lang)); });
  }
  function set(l) {
    lang = l; try { localStorage.setItem(KEY, l); } catch (e) {}
    D.documentElement.lang = l === 'hi' ? 'hi' : 'en';
    if (l === 'hi') font();
    paintToggle(); all();
    D.dispatchEvent(new CustomEvent('karsha-lang', {detail: l}));
  }
  function toggle() {
    if (D.querySelector('.kr-lang')) return;
    var t = D.createElement('div'); t.className = 'kr-lang'; t.setAttribute('data-noi18n', ''); t.setAttribute('role', 'group'); t.setAttribute('aria-label', 'Language');
    t.innerHTML = '<button type="button" data-l="en" aria-pressed="false">English</button><button type="button" data-l="hi" aria-pressed="false" lang="hi">हिन्दी</button>';
    t.addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) set(b.dataset.l); });
    D.body.appendChild(t); paintToggle();
  }
  window.karshaLang = {get: function () { return lang; }, set: set, tr: function (s) { var r = tr(s); return r === null ? s : r; }};

  function boot() {
    toggle(); D.documentElement.lang = lang === 'hi' ? 'hi' : 'en'; if (lang === 'hi') font();
    fetch(base + 'hi.json').then(function (r) { return r.json(); }).then(function (j) {
      dict = {s: j.s, rx: (j.r || []).map(function (p) { return [new RegExp(p[0]), p[1]]; })};
      ready = true;
      mo.observe(D.body, {childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATTRS});
      if (lang === 'hi') { var go = function () { all(); }; if (D.readyState === 'complete') setTimeout(go, 900); else window.addEventListener('load', function () { setTimeout(go, 900); }); }
    }).catch(function () {});
  }
  if (D.readyState === 'loading') D.addEventListener('DOMContentLoaded', boot); else boot();
})();
