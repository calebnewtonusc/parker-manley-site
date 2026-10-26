// Item 9: Parker's Mac. The menu bar clock, the Chrome window's history and
// its three pages, and the ManleyGram post viewer. window.desk is the hook
// the end card uses to grow the Contact tab into the frame.
(() => {
  const desk = document.querySelector(".desk");
  if (!desk) return;

  // The clock reads the visitor's own time, the way their menu bar does.
  const clock = desk.querySelector(".mb__clock");
  const narrow = matchMedia("(max-width: 760px)");
  const tick = () => {
    const now = new Date();
    const time = now.toLocaleTimeString([], {
      hour: "numeric",
      minute: "2-digit",
    });
    if (narrow.matches) {
      clock.textContent = time;
    } else {
      const day = now
        .toLocaleDateString([], {
          weekday: "short",
          month: "short",
          day: "numeric",
        })
        .replace(/,/g, "");
      clock.textContent = `${day}  ${time}`;
    }
    clock.dateTime = now.toISOString();
    setTimeout(
      tick,
      60000 - (now.getSeconds() * 1000 + now.getMilliseconds()) + 20,
    );
  };
  tick();
  narrow.addEventListener("change", tick);

  // Chrome.
  const cw = desk.querySelector(".cw");
  const url = cw.querySelector(".cw__url");
  const back = cw.querySelector(".cw__back");
  const fwd = cw.querySelector(".cw__fwd");
  const pages = Object.fromEntries(
    [...cw.querySelectorAll(".cw__page")].map((p) => [p.dataset.page, p]),
  );
  const tabs = [...cw.querySelectorAll(".cw__tab")];
  const flix = pages.flix;
  const billV = flix.querySelector(".mfx__bill-v");
  const META = {
    ntp: { title: "New Tab", url: "" },
    flix: { title: "ManleyFlix", url: "manleyflix.com/browse" },
    contact: { title: "Contact Parker Manley", url: "contactparkermanley.com" },
    gram: {
      title: "Parker Manley (@parkermanley) • ManleyGram photos and videos",
      url: "manleygram.com/parkermanley/",
    },
  };
  const stack = ["flix"];
  let at = 0;

  const show = (name) => {
    closeViewer(true);
    cw.dataset.at = name;
    Object.entries(pages).forEach(([k, p]) => {
      p.hidden = k !== name;
    });
    pages[name].scrollTop = 0;
    url.value = META[name].url;
    tabs.forEach((t) => t.classList.toggle("is-on", t.dataset.go === name));
    document.dispatchEvent(new CustomEvent("desk:page", { detail: name }));
    back.disabled = at === 0;
    fwd.disabled = at === stack.length - 1;
    if (name === "flix") {
      if (!billV.src) billV.src = billV.dataset.src;
      billV.play().catch(() => {});
    } else billV.pause();
  };
  const go = (name) => {
    if (!pages[name]) return;
    if (stack[at] === name) {
      pages[name].scrollTo({ top: 0, behavior: "smooth" });
      return;
    }
    stack.splice(at + 1);
    stack.push(name);
    at = stack.length - 1;
    show(name);
  };
  back.addEventListener("click", () => {
    if (at > 0) show(stack[--at]);
  });
  fwd.addEventListener("click", () => {
    if (at < stack.length - 1) show(stack[++at]);
  });
  cw.querySelector(".cw__reload").addEventListener("click", () =>
    show(stack[at]),
  );
  desk
    .querySelectorAll("[data-go]")
    .forEach((b) => b.addEventListener("click", () => go(b.dataset.go)));

  // Typing in the omnibox or the Manleygle box goes to whichever of the two
  // sites the words point at.
  const route = (q) =>
    /contact|hire|email/i.test(q) ? "contact" : /gram|photo|insta|pic|parkermanley/i.test(q) ? "gram" : "flix";
  cw.querySelector(".cw__omni").addEventListener("submit", (ev) => {
    ev.preventDefault();
    const q = url.value.trim();
    url.blur();
    if (q) go(route(q));
    else show(stack[at]);
  });
  url.addEventListener("focus", () => url.select());
  url.addEventListener("blur", () => {
    url.value = META[stack[at]].url;
  });

  // Netflix darkens its header once the billboard scrolls under it.
  flix.addEventListener(
    "scroll",
    () => flix.classList.toggle("is-scrolled", flix.scrollTop > 8),
    { passive: true },
  );

  // ManleyGram post viewer.
  const gram = pages.gram;
  // The viewer pages through whichever set it was opened from: the posts
  // grid, the tagged grid, or a highlight.
  let tiles = [];
  const viewer = cw.querySelector(".igv");
  const vImg = viewer.querySelector(".igv__img");
  const vMedia = viewer.querySelector(".igv__media");
  const like = viewer.querySelector(".igv__like");
  const save = viewer.querySelector(".igv__save");
  let cur = -1;
  let opener = null;

  const paint = (i) => {
    cur = (i + tiles.length) % tiles.length;
    const t = tiles[cur];
    vMedia.style.setProperty("--ar", `${t.dataset.w} / ${t.dataset.h}`);
    viewer.style.setProperty("--arn", String(t.dataset.w / t.dataset.h));
    vImg.src = t.dataset.full;
    like.setAttribute("aria-pressed", "false");
    save.setAttribute("aria-pressed", "false");
    [-1, 1].forEach((d) => {
      const n = tiles[(cur + d + tiles.length) % tiles.length];
      new Image().src = n.dataset.full;
    });
  };
  const openViewer = (i, set, from) => {
    if (set) tiles = set;
    opener = from || tiles[i];
    paint(i);
    viewer.hidden = false;
    viewer.scrollTop = 0;
    requestAnimationFrame(() => viewer.classList.add("is-on"));
    viewer.querySelector(".igv__x").focus({ preventScroll: true });
  };
  function closeViewer(now) {
    if (viewer.hidden) return;
    viewer.classList.remove("is-on");
    const done = () => {
      viewer.hidden = true;
      vImg.removeAttribute("src");
    };
    if (now === true) done();
    else setTimeout(done, 170);
    if (opener && now !== true) opener.focus({ preventScroll: true });
  }

  gram.querySelectorAll(".ig-grid").forEach((grid) => {
    const set = [...grid.querySelectorAll(".ig-tile")];
    set.forEach((t, i) => t.addEventListener("click", () => openViewer(i, set)));
  });
  // Highlights: each opens its own run of photographs.
  gram.querySelectorAll(".ig-hl").forEach((h) => {
    const set = h.dataset.set.split(",").map((x) => {
      const [full, w, hh] = x.split("|");
      return { dataset: { full, w, h: hh }, focus: () => h.focus({ preventScroll: true }) };
    });
    h.addEventListener("click", () => openViewer(0, set, h));
  });
  // Posts / Reels / Tagged.
  const tabBtns = [...gram.querySelectorAll(".ig-tabs [data-tab]")];
  tabBtns.forEach((b) => b.addEventListener("click", () => {
    tabBtns.forEach((x) => x.classList.toggle("is-on", x === b));
    gram.querySelectorAll("[data-grid]").forEach((g) => { g.hidden = g.dataset.grid !== b.dataset.tab; });
  }));
  viewer.querySelector(".igv__x").addEventListener("click", closeViewer);
  viewer.querySelector(".igv__back").addEventListener("click", closeViewer);
  viewer
    .querySelector(".igv__nav--p")
    .addEventListener("click", () => paint(cur - 1));
  viewer
    .querySelector(".igv__nav--n")
    .addEventListener("click", () => paint(cur + 1));
  viewer.addEventListener("click", (ev) => {
    if (ev.target === viewer) closeViewer();
  });
  like.addEventListener("click", () => {
    const on = like.getAttribute("aria-pressed") !== "true";
    like.setAttribute("aria-pressed", String(on));
    like.classList.remove("is-pop");
    if (on) requestAnimationFrame(() => like.classList.add("is-pop"));
  });
  vImg.addEventListener("dblclick", () => {
    if (like.getAttribute("aria-pressed") !== "true") like.click();
  });
  save.addEventListener("click", () =>
    save.setAttribute(
      "aria-pressed",
      String(save.getAttribute("aria-pressed") !== "true"),
    ),
  );
  addEventListener("keydown", (ev) => {
    if (viewer.hidden) return;
    if (ev.key === "ArrowLeft") paint(cur - 1);
    else if (ev.key === "ArrowRight") paint(cur + 1);
    else if (ev.key === "Escape") {
      ev.stopImmediatePropagation();
      closeViewer();
    }
  });
  // A swipe on the photo steps through the posts on a phone.
  let sx = null;
  vMedia.addEventListener("pointerdown", (ev) => {
    if (ev.pointerType !== "mouse") sx = ev.clientX;
  });
  vMedia.addEventListener("pointerup", (ev) => {
    if (sx === null) return;
    const dx = ev.clientX - sx;
    sx = null;
    if (Math.abs(dx) > 40) paint(cur + (dx < 0 ? 1 : -1));
  });

  show("flix");

  window.desk = {
    el: desk,
    open: go,
    page: () => stack[at],
    contactRect: () => pages.contact.querySelector(".cpm__shot").getBoundingClientRect(),
  };
})();
