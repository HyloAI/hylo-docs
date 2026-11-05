// Package indexes replaced monolithic API pages. Forward existing symbol links to
// the corresponding module while leaving package and module-index anchors intact.
(() => {
  function followSymbol() {
    let symbol;
    try {
      symbol = decodeURIComponent(window.location.hash.slice(1));
    } catch {
      return;
    }
    if (!symbol || document.getElementById(symbol)) return;
    const candidates = [...document.querySelectorAll("a[data-api-module]")]
      .filter((link) => symbol === link.dataset.apiModule || symbol.startsWith(`${link.dataset.apiModule}.`))
      .sort((a, b) => b.dataset.apiModule.length - a.dataset.apiModule.length);
    if (!candidates.length) return;
    const target = new URL(candidates[0].href, window.location.href);
    target.hash = symbol;
    window.location.replace(target.href);
  }
  followSymbol();
  window.addEventListener("hashchange", followSymbol);
})();
