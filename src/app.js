// One file for every page. Each block checks its element exists first.
(() => {
  const fine = matchMedia("(hover: hover) and (pointer: fine)").matches;
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const small = matchMedia("(max-width: 700px)").matches;

  // Phones get the lighter encode.
  document.querySelectorAll("video[data-src]").forEach((v) => {
    v.src = small && v.dataset.srcSmall ? v.dataset.srcSmall : v.dataset.src;
    v.addEventListener("loadeddata", () => { if (v.paused && v.currentTime < 0.5) v.currentTime = 0.5; }, { once: true });
  });

  // Same-page anchors glide instead of jumping.
  document.addEventListener("click", (e) => {
    const a = e.target.closest('a[href^="#"]');
    if (!a) return;
    const target = document.querySelector(a.getAttribute("href"));
    if (!target) return;
    e.preventDefault();
    const top = target.getBoundingClientRect().top + scrollY - 64;
    scrollTo({ top, behavior: reduced ? "auto" : "smooth" });
    history.replaceState(null, "", a.getAttribute("href"));
  });

  // Reel: muted loop, one toggle for sound, pauses when off screen.
  const reel = document.querySelector("#reel");
  const sound = document.querySelector(".sound");
  if (reel && sound) {
    const label = sound.querySelector(".label");
    sound.addEventListener("click", () => {
      const on = sound.getAttribute("aria-pressed") !== "true";
      reel.muted = !on;
      if (on) {
        reel.currentTime = 0;
        reel.play().catch(() => {});
      }
      sound.setAttribute("aria-pressed", String(on));
      label.textContent = on ? "Sound on" : "Sound off";
    });
    new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) reel.play().catch(() => {});
        else reel.pause();
      },
      { threshold: 0.2 },
    ).observe(reel);
  }

  // Now Showing: the programme picks which loop the screen plays.
  const screen = document.querySelector(".screen");
  if (screen) {
    const films = JSON.parse(
      document.querySelector("#showing-data").textContent,
    );
    const videos = [...screen.querySelectorAll("video")];
    const items = [...document.querySelectorAll(".programme a")];
    const meta = document.querySelector(".now__meta");
    const title = document.querySelector(".now__title");
    const syn = document.querySelector(".now__syn");
    const fest = document.querySelector(".now__fest");
    const watch = document.querySelector(".now__watch");
    let current = 0;
    let visible = false;

    const select = (i) => {
      if (i === current && videos[i].classList.contains("is-on")) return;
      const f = films[i];
      videos[current].pause();
      videos.forEach((v, k) => v.classList.toggle("is-on", k === i));
      items.forEach((a, k) => a.setAttribute("aria-current", String(k === i)));
      current = i;
      if (visible) videos[i].play().catch(() => {});
      meta.textContent = f.meta;
      title.textContent = f.title;
      syn.textContent = f.synopsis;
      fest.textContent = f.festivals;
      watch.href = f.href;
      screen.href = f.href;
      screen.setAttribute("aria-label", `Watch ${f.title}`);
    };

    items.forEach((a, i) => {
      if (fine) a.addEventListener("mouseenter", () => select(i));
      a.addEventListener("focus", () => select(i));
      // On touch, the first tap previews and the second opens the film.
      a.addEventListener("click", (e) => {
        if (!fine && current !== i) {
          e.preventDefault();
          select(i);
        }
      });
    });

    new IntersectionObserver(
      ([entry]) => {
        visible = entry.isIntersecting;
        if (visible) videos[current].play().catch(() => {});
        else videos[current].pause();
      },
      { threshold: 0.25 },
    ).observe(screen);
    // A loop that finishes loading after the screen came into view starts then.
    videos.forEach((v, k) => v.addEventListener("canplay", () => {
      if (visible && k === current && v.paused) v.play().catch(() => {});
    }));

    // The cursor becomes the play button over the screen.
    if (fine) {
      const pill = screen.querySelector(".screen__play");
      screen.addEventListener("mouseenter", () =>
        screen.classList.add("is-hover"),
      );
      screen.addEventListener("mouseleave", () =>
        screen.classList.remove("is-hover"),
      );
      screen.addEventListener("mousemove", (e) => {
        const r = screen.getBoundingClientRect();
        pill.style.left = `${e.clientX - r.left}px`;
        pill.style.top = `${e.clientY - r.top}px`;
      });
    }
    select(0);
  }

  // Film page: the YouTube player loads only when asked for.
  const player = document.querySelector(".player[data-yt]");
  if (player) {
    const btn = player.querySelector("button");
    btn.addEventListener("click", () => {
      const f = document.createElement("iframe");
      f.src = `https://www.youtube-nocookie.com/embed/${player.dataset.yt}?autoplay=1&rel=0&modestbranding=1&playsinline=1`;
      f.title = btn.getAttribute("aria-label");
      f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
      f.allowFullscreen = true;
      player.replaceChildren(f);
    });
  }

  // Contact form posts to FormSubmit, which forwards to Parker's inbox.
  const form = document.querySelector(".form");
  if (form) {
    const status = form.querySelector(".form__status");
    const button = form.querySelector("button[type=submit]");
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (form.querySelector(".hp input").value) return;
      button.disabled = true;
      status.dataset.state = "";
      status.textContent = "Sending...";
      try {
        const res = await fetch(form.action, {
          method: "POST",
          headers: { Accept: "application/json" },
          body: new FormData(form),
        });
        if (!res.ok) throw new Error(String(res.status));
        form.reset();
        status.dataset.state = "ok";
        status.textContent = "Sent. I'll get back to you soon.";
      } catch (err) {
        status.dataset.state = "err";
        status.textContent =
          "That didn't send. Email me directly at the address above.";
        console.error("contact form", err);
      } finally {
        button.disabled = false;
      }
    });
  }

  // Photography: size toggle and a keyboard-friendly lightbox.
  const sheet = document.querySelector(".sheet");
  if (sheet) {
    document.querySelectorAll(".sizes button").forEach((b) => {
      b.addEventListener("click", () => {
        sheet.dataset.size = b.dataset.size;
        document
          .querySelectorAll(".sizes button")
          .forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      });
    });
    const shots = [...sheet.querySelectorAll("button")];
    const box = document.querySelector(".lightbox");
    const img = box.querySelector("img");
    let at = 0;
    let opener = null;
    const show = (i) => {
      at = (i + shots.length) % shots.length;
      img.src = shots[at].dataset.full;
      img.alt = shots[at].querySelector("img").alt;
    };
    const close = () => {
      box.classList.remove("is-open");
      document.body.style.overflow = "";
      if (opener) opener.focus();
    };
    shots.forEach((s, i) =>
      s.addEventListener("click", () => {
        opener = s;
        show(i);
        box.classList.add("is-open");
        document.body.style.overflow = "hidden";
        box.querySelector(".x").focus();
      }),
    );
    box.querySelector(".x").addEventListener("click", close);
    box.querySelector(".pv").addEventListener("click", () => show(at - 1));
    box.querySelector(".nx").addEventListener("click", () => show(at + 1));
    box.addEventListener("click", (e) => {
      if (e.target === box) close();
    });
    addEventListener("keydown", (e) => {
      if (!box.classList.contains("is-open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") show(at - 1);
      if (e.key === "ArrowRight") show(at + 1);
    });
  }
})();
