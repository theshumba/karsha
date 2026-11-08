/* Written by docs/harden.py.

   Framer's client-side router tries to render the next page from the current
   page's prefetch cache. When the next page needs collection data the cache
   does not hold, the CMS asks for a byte range, which only Framer's own CDN
   serves. Every page here is a complete document, so a normal page load is both
   correct and cheaper.

   Relative hrefs (./projects/thing) are also resolved against the page's own
   slash-less path, so the site behaves the same whether the host adds a
   trailing slash or not. */
var BASE = "/karsha";
document.addEventListener("click", function (e) {
  if (e.defaultPrevented || e.button !== 0) return;
  if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  var a = e.target && e.target.closest && e.target.closest("a[href]");
  if (!a) return;
  var href = a.getAttribute("href");
  if (!href || href.indexOf("#") !== -1) return;
  if (a.target && a.target !== "_self") return;
  var target;
  if (href.charAt(0) === "/") {
    target = (href === BASE || href.indexOf(BASE + "/") === 0) ? href : BASE + href;
  } else if (href.charAt(0) === ".") {
    var here = location.pathname.replace(/\/$/, "");
    var dir = here.slice(0, here.lastIndexOf("/") + 1) || "/";
    try {
      target = new URL(href, location.origin + dir).pathname;
    } catch (err) { return; }
  } else {
    return;
  }
  e.stopPropagation();
  e.preventDefault();
  window.location.assign(target);
}, true);

/* Site is served under /karsha/. Keep every root-absolute link inside it, including ones the
   page scripts write after load, so new-tab and middle-click behave too. */
(function () {
  var BASE = "/karsha";
  function fix(root) {
    var as = (root.querySelectorAll ? root.querySelectorAll('a[href^="/"]') : []);
    for (var i = 0; i < as.length; i++) {
      var h = as[i].getAttribute("href");
      if (h.indexOf("//") === 0 || h === BASE || h.indexOf(BASE + "/") === 0) continue;
      as[i].setAttribute("href", BASE + h);
    }
  }
  function go() { fix(document); new MutationObserver(function (ms) { for (var i = 0; i < ms.length; i++) { for (var j = 0; j < ms[i].addedNodes.length; j++) { var n = ms[i].addedNodes[j]; if (n.nodeType === 1) { if (n.matches && n.matches('a[href^="/"]')) fix({querySelectorAll: function () { return [n]; }}); fix(n); } } if (ms[i].type === "attributes") fix(ms[i].target.parentNode || document); } }).observe(document.documentElement, {childList: true, subtree: true, attributes: true, attributeFilter: ["href"]}); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", go); else go();
})();
