// Keep full content in the built HTML for search and readers without JavaScript.
// Enhance explicitly marked reference sections and generated API members only.
(() => {
  const article = document.querySelector("article.md-content__inner");
  if (!article) return;

  function disclosure(heading) {
    const details = document.createElement("details");
    details.className = "hylo-content-details";
    const summary = document.createElement("summary");
    heading.before(details);
    details.append(summary);
    summary.append(heading);
    return details;
  }

  article.querySelectorAll(".hylo-collapsible").forEach((heading) => {
    const level = Number(heading.tagName.slice(1));
    let sibling = heading.nextElementSibling;
    const details = disclosure(heading);
    while (sibling) {
      if (/^H[1-6]$/.test(sibling.tagName) && Number(sibling.tagName.slice(1)) <= level) break;
      const next = sibling.nextElementSibling;
      details.append(sibling);
      sibling = next;
    }
  });

  article.querySelectorAll(".doc-object:not(.doc-module)").forEach((object) => {
    const heading = object.querySelector(":scope > .doc-heading");
    if (!heading) return;
    const details = disclosure(heading);
    [...object.childNodes].forEach((node) => {
      if (node !== details) details.append(node);
    });
  });

  function reveal(hash) {
    let target;
    try {
      target = document.getElementById(decodeURIComponent(hash.slice(1)));
    } catch {
      return;
    }
    if (!target || !article.contains(target)) return;
    let details = target.closest("details");
    while (details) {
      details.open = true;
      details = details.parentElement.closest("details");
    }
    // Opening ancestors and wrapping sections changes the target's position.
    requestAnimationFrame(() => target.scrollIntoView());
  }

  reveal(window.location.hash);
  window.addEventListener("hashchange", () => reveal(window.location.hash));
  document.addEventListener("click", (event) => {
    const link = event.target.closest("a[href]");
    if (!link || event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const url = new URL(link.href);
    if (url.origin === location.origin && url.pathname === location.pathname && url.search === location.search && url.hash) {
      reveal(url.hash);
    }
  });
})();
