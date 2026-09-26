(function () {
  "use strict";
  var app = document.getElementById("app");
  var reduceMQ = window.matchMedia("(prefers-reduced-motion: reduce)");
  var motion = !reduceMQ.matches && "IntersectionObserver" in window;
  if (motion) app.classList.add("motion");
  if (reduceMQ.addEventListener) reduceMQ.addEventListener("change", function () { location.reload(); });

  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }

  var header = $(".site-header");
  var menuBtn = $(".menu-btn");
  var nav = $("#main-nav");

  /* ---------- Mobile menu ---------- */
  function setMenu(open, returnFocus) {
    menuBtn.setAttribute("aria-expanded", String(open));
    nav.classList.toggle("is-open", open);
    if (open) { var first = nav.querySelector("a"); if (first) first.focus(); }
    else if (returnFocus) menuBtn.focus();
  }
  menuBtn.addEventListener("click", function () { setMenu(menuBtn.getAttribute("aria-expanded") !== "true"); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && menuBtn.getAttribute("aria-expanded") === "true") setMenu(false, true);
  });
  document.addEventListener("click", function (e) {
    if (menuBtn.getAttribute("aria-expanded") === "true" && !header.contains(e.target)) setMenu(false);
  });

  /* ---------- Split headings into words (visual copy is aria-hidden; real text stays for screen readers) ---------- */
  function splitHeading(h) {
    if (h.dataset.split) return;
    h.dataset.split = "1";
    var sr = document.createElement("span");
    sr.className = "sr-only";
    sr.textContent = h.textContent.replace(/\s+/g, " ").trim();
    var vis = document.createElement("span");
    vis.className = "split";
    vis.setAttribute("aria-hidden", "true");
    while (h.firstChild) vis.appendChild(h.firstChild);
    var i = 0;
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(" ")); return; }
            var w = document.createElement("span"); w.className = "w";
            var wi = document.createElement("span"); wi.className = "wi"; wi.style.setProperty("--i", i++);
            wi.textContent = part; w.appendChild(wi); frag.appendChild(w);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1) { walk(n); }
      });
    })(vis);
    h.appendChild(sr);
    h.appendChild(vis);
  }

  /* ---------- Reveal on scroll: only below-the-fold content waits; nothing stays hidden without JS ---------- */
  var io = motion ? new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) { en.target.classList.remove("rv-wait"); io.unobserve(en.target); }
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0 }) : null;

  function armReveals(root, entrance) {
    if (!motion) return;
    var vh = window.innerHeight;
    $$(".rv, .rv-img, .rv-split", root).forEach(function (el) {
      if (el.closest("[hidden]")) return;
      if (el.classList.contains("rv-split")) splitHeading(el);
      var r = el.getBoundingClientRect();
      var inView = r.top < vh * 0.94 && r.bottom > 0;
      if (inView && !entrance) { el.classList.remove("rv-wait"); return; }
      el.classList.add("rv-wait");
      if (inView) {
        requestAnimationFrame(function () { requestAnimationFrame(function () { el.classList.remove("rv-wait"); }); });
      } else {
        io.observe(el);
      }
    });
  }
  // Keyboard users never land on something invisible
  document.addEventListener("focusin", function (e) {
    var el = e.target.closest ? e.target.closest(".rv-wait") : null;
    while (el) { el.classList.remove("rv-wait"); el = el.parentElement ? el.parentElement.closest(".rv-wait") : null; }
  });

  /* ---------- Subtle photo parallax below the hero (scroll-linked only, never autonomous) ---------- */
  var parEls = $$("[data-par]");
  var ticking = false;
  function frame() {
    ticking = false;
    header.classList.toggle("is-scrolled", window.scrollY > 4);
    if (!motion) return;
    var vh = window.innerHeight;
    parEls.forEach(function (el) {
      if (el.offsetParent === null) return;
      var ref = el.parentElement.getBoundingClientRect();
      if (ref.bottom < -120 || ref.top > vh + 120) return;
      var c = ref.top + ref.height / 2 - vh / 2;
      el.style.translate = "0 " + clamp(-c * parseFloat(el.dataset.par), -48, 48).toFixed(1) + "px";
    });
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);

  /* ---------- Hero video: autoplays only with motion welcome, always pausable, pauses off-screen ---------- */
  var video = $("#hero-video"), vBtn = $("#video-toggle"), userPaused = false, videoVisible = true;
  function setVideoUI(playing) {
    var label = playing ? "Video anhalten" : "Video abspielen";
    vBtn.querySelector("span").textContent = label;
    vBtn.title = label;
    vBtn.querySelector("use").setAttribute("href", playing ? "#i-pause" : "#i-play");
  }
  function playVideo() { var pr = video.play(); if (pr && pr.catch) pr.catch(function () { setVideoUI(false); }); }
  function syncVideo() {
    var should = motion && !userPaused && videoVisible;
    if (should && video.paused) playVideo();
    else if (!should && !video.paused) video.pause();
  }
  if (video && vBtn) {
    vBtn.addEventListener("click", function () {
      if (video.paused) { userPaused = false; playVideo(); } else { userPaused = true; video.pause(); }
    });
    video.addEventListener("play", function () { setVideoUI(true); });
    video.addEventListener("pause", function () { setVideoUI(false); });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) { videoVisible = en[0].isIntersecting; syncVideo(); }).observe(video);
    }
  }

  /* ---------- Skip link: move focus to the page heading ---------- */
  var skip = $("[data-skip]");
  if (skip) skip.addEventListener("click", function (e) {
    var h = $("main h1");
    if (!h) return;
    e.preventDefault();
    h.focus();
    h.scrollIntoView({ block: "start" });
  });

  /* ---------- Forms: accessible validation, preview success ---------- */
  var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  function fieldError(input, msg) {
    var wrap = input.closest(".field");
    var old = wrap.querySelector(".err");
    if (old) old.remove();
    input.removeAttribute("aria-invalid");
    input.removeAttribute("aria-describedby");
    if (!msg) return;
    var p = document.createElement("p");
    p.className = "err";
    p.id = input.id + "-err";
    p.innerHTML = '<svg class="icon" aria-hidden="true"><use href="#i-alert"/></svg><span></span>';
    p.querySelector("span").textContent = msg;
    wrap.appendChild(p);
    input.setAttribute("aria-invalid", "true");
    input.setAttribute("aria-describedby", p.id);
  }
  function validate(input) {
    var v = input.value.trim();
    if (input.required && !v) return input.dataset.msg || "Bitte füllen Sie dieses Feld aus.";
    if (input.type === "email" && v && !emailRe.test(v)) return "Bitte prüfen Sie die E-Mail-Adresse, z. B. name@beispiel.de.";
    return "";
  }
  $$("form[data-done]").forEach(function (form) {
    var summary = form.querySelector(".form-summary");
    var inputs = $$('input:not([type="hidden"]):not([name="bot-field"]),textarea', form);
    inputs.forEach(function (inp) {
      // Clear an error once the input is valid (while typing, not on blur, so the submit button never jumps under the pointer)
      inp.addEventListener("input", function () { if (inp.getAttribute("aria-invalid") && !validate(inp)) fieldError(inp, ""); });
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var errors = [];
      inputs.forEach(function (inp) {
        var msg = validate(inp);
        fieldError(inp, msg);
        if (msg) errors.push({ id: inp.id, label: form.querySelector('label[for="' + inp.id + '"]').firstChild.textContent.trim(), msg: msg });
      });
      if (errors.length) {
        summary.hidden = false;
        summary.innerHTML = "<h3></h3><ul></ul>";
        summary.querySelector("h3").textContent = errors.length === 1 ? "Bitte prüfen Sie 1 Angabe:" : "Bitte prüfen Sie " + errors.length + " Angaben:";
        var ul = summary.querySelector("ul");
        errors.forEach(function (er) {
          var li = document.createElement("li");
          var a = document.createElement("a");
          a.href = "#" + er.id;
          a.setAttribute("data-field", er.id);
          a.textContent = er.label + ": " + er.msg;
          li.appendChild(a);
          ul.appendChild(li);
        });
        summary.focus();
        return;
      }
      summary.hidden = true;
      var btn = form.querySelector('[type="submit"]');
      if (btn) btn.disabled = true;
      fetch("/", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams(new FormData(form)).toString()
      }).then(function (res) {
        if (!res.ok) throw new Error(res.status);
        var done = document.createElement("div");
        done.className = "form-done";
        done.setAttribute("role", "status");
        done.setAttribute("tabindex", "-1");
        done.innerHTML = '<span class="done-ic"><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg></span><p></p>';
        done.querySelector("p").textContent = form.dataset.done;
        form.replaceWith(done);
        done.focus();
      }).catch(function () {
        if (btn) btn.disabled = false;
        summary.hidden = false;
        summary.innerHTML = "<h3></h3><p></p>";
        summary.querySelector("h3").textContent = "Das Senden hat leider nicht geklappt.";
        summary.querySelector("p").textContent = "Bitte versuchen Sie es erneut oder rufen Sie uns an: 030 3758 0867.";
        summary.focus();
      });
    });
  });
  // Error-summary links focus their field instead of routing
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a[data-field]");
    if (!a) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    var f = document.getElementById(a.dataset.field);
    if (f) { f.focus(); f.scrollIntoView({ block: "center" }); }
  }, true);

  /* ---------- Ratgeber search: full text of every article (index loaded on first search) ---------- */
  var sForm = $("#rg-search"), sOut = $("#rg-results"), posts = null;
  function render(q) {
    sOut.hidden = false;
    sOut.innerHTML = "";
    var h = document.createElement("h2");
    if (!q) { h.textContent = "Bitte geben Sie einen Suchbegriff ein."; sOut.appendChild(h); return; }
    var ql = q.toLowerCase();
    var hits = posts.filter(function (p) { return (p.t + " " + p.c + " " + p.x).toLowerCase().indexOf(ql) !== -1; });
    h.textContent = hits.length ? hits.length + (hits.length === 1 ? " Beitrag" : " Beiträge") + " zu „" + q + "“" : "Keine Beiträge zu „" + q + "“ gefunden.";
    sOut.appendChild(h);
    if (hits.length) {
      var ul = document.createElement("ul");
      hits.forEach(function (p) {
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.href = p.u;
        a.textContent = p.t;
        li.appendChild(a);
        ul.appendChild(li);
      });
      sOut.appendChild(ul);
    }
  }
  if (sForm) sForm.addEventListener("submit", function (e) {
    e.preventDefault();
    var q = $("#rg-q").value.trim();
    if (posts) { render(q); return; }
    fetch(sForm.dataset.index).then(function (r) { return r.json(); }).then(function (d) { posts = d; render(q); })
      .catch(function () { sOut.hidden = false; sOut.textContent = "Die Suche ist gerade nicht verfügbar."; });
  });

  /* ---------- Boot ---------- */
  armReveals(document.getElementById("main"), false);
  frame();
})();
