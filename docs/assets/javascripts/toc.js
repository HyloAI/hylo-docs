// Reveal a linked heading in both the desktop and mobile tables of contents.
(() => {
  function revealHash() {
    let hash;
    try {
      hash = decodeURIComponent(window.location.hash);
    } catch {
      return;
    }
    if (!hash) return;
    document.querySelectorAll(".md-nav--secondary a[href]").forEach((link) => {
      if (decodeURIComponent(link.hash) !== hash) return;
      let group = link.closest("details.hylo-toc-group");
      while (group) {
        group.open = true;
        group = group.parentElement.closest("details.hylo-toc-group");
      }
    });
  }
  revealHash();
  window.addEventListener("hashchange", revealHash);
})();
