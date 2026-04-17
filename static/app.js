// Keep JS minimal: add a small "active section" feel and safe smooth scroll for older browsers.
(function () {
  const links = Array.from(document.querySelectorAll('a[href^="#"]'));
  for (const a of links) {
    a.addEventListener("click", (e) => {
      const id = a.getAttribute("href");
      if (!id || id === "#") return;
      const el = document.querySelector(id);
      if (!el) return;
      e.preventDefault();
      el.scrollIntoView({ behavior: "smooth", block: "start" });
      history.pushState(null, "", id);
    });
  }
})();
