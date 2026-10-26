// One file for every page. Each block checks its element exists first.
(() => {
  const fine = matchMedia("(hover: hover) and (pointer: fine)").matches;
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const small = matchMedia("(max-width: 700px)").matches;

  // Phones get the lighter encode. Each loop opens on a fade from black, so a
  // paused one is parked just past it instead of showing a black frame.
  document.querySelectorAll("video[data-src]").forEach((v) => {
    v.src = small && v.dataset.srcSmall ? v.dataset.srcSmall : v.dataset.src;
    v.addEventListener(
      "loadeddata",
      () => {
        if (v.paused && v.currentTime < 0.5) v.currentTime = 0.5;
      },
      { once: true },
    );
  });

  // If the browser blocked autoplay, the first touch starts what's on screen.
  addEventListener(
    "touchstart",
    () => {
      document.querySelectorAll("#reel, .scene__bg video.is-on").forEach((v) => {
        if (v.paused) v.play().catch(() => {});
      });
    },
    { once: true, passive: true },
  );

  const glide = (top) =>
    scrollTo({ top, behavior: reduced ? "auto" : "smooth" });

  // Sound: score.js (Web Audio, real recordings when present) does the
  // work. This adapter keeps the call sites short.
  const sfx = (() => {
    const S = () => window.score;
    const play = (name, opts) => { const sc = S(); if (sc) sc.play(name, opts); };
    return {
      get on() { const sc = S(); return sc ? sc.on : true; },
      set(v) { const sc = S(); if (sc) sc.on = v; },
      wake() { const sc = S(); if (sc) sc.unlock(); },
      // The real leader only pops on the 2.
      beep(k) { if (k === 2) play("pop2"); },
      clatter(sec) { play("clatter", { dur: sec }); },
      rip() { play("rip"); },
      flap(n) { play("flap", { n }); },
      stamp() { play("stamp"); },
      rec() { play("rec"); },
      servo() { play("servo"); },
      tick() { play("tick"); },
      whoosh() { play("whoosh"); },
      chk() { play("chk"); },
      clack() { play("clack"); },
      // After the last frame: the tail-pop, then the film flapping on the reel.
      runout() { play("tailpop", { at: 0.6 }); play("runout", { at: 0.9 }); },
    };
  })();

  // Academy leader: Roll film, then 3, 2, 1 with the sweep, the beep on every
  // number and the projector running. Once per visit; scrolling skips it.
  const reelEl = document.querySelector("#reel");
  const soundBtn = document.querySelector(".sound");
  const setReelSound = (v) => {
    if (!reelEl || !soundBtn) return;
    reelEl.muted = !v;
    soundBtn.setAttribute("aria-pressed", String(v));
    soundBtn.querySelector(".label").textContent = v ? "Sound on" : "Sound off";
  };
  const leader = document.querySelector(".leader");
  if (leader) {
    let seen = false;
    try { seen = sessionStorage.getItem("leader") === "1"; } catch (err) { seen = false; }
    if (seen || reduced || location.hash) leader.remove();
    else {
      try { sessionStorage.setItem("leader", "1"); } catch (err) { /* private mode */ }
      const num = leader.querySelector(".leader__n");
      // The print: grain, dust, hairs and scratches redrawn at 24 fps, the
      // way a worn leader looks running through a projector.
      const dirt = leader.querySelector(".leader__dirt");
      const dc = dirt.getContext("2d");
      const grain = document.createElement("canvas");
      grain.width = 200;
      grain.height = 200;
      const gc = grain.getContext("2d");
      const gimg = gc.createImageData(200, 200);
      let lastDraw = 0;
      let scratchX = Math.random();
      const paint = (t) => {
        if (!leader.isConnected) return;
        requestAnimationFrame(paint);
        if (t - lastDraw < 1000 / 24) return;
        lastDraw = t;
        const w = (dirt.width = Math.round(innerWidth / 2));
        const h = (dirt.height = Math.round(innerHeight / 2));
        for (let i = 0; i < gimg.data.length; i += 4) {
          const v = Math.random() * 255;
          gimg.data[i] = gimg.data[i + 1] = gimg.data[i + 2] = v;
          gimg.data[i + 3] = 46;
        }
        gc.putImageData(gimg, 0, 0);
        dc.drawImage(grain, 0, 0, w, h);
        dc.fillStyle = "rgba(20, 18, 14, 0.85)";
        for (let i = 0; i < 9; i++) {
          dc.beginPath();
          dc.arc(Math.random() * w, Math.random() * h, Math.random() * 2.4 + 0.4, 0, 6.3);
          dc.fill();
        }
        // A hair now and then, curled, on the frame for a beat.
        if (Math.random() < 0.25) {
          dc.strokeStyle = "rgba(20, 18, 14, 0.7)";
          dc.lineWidth = 1;
          dc.beginPath();
          let x = Math.random() * w;
          let y = Math.random() * h;
          dc.moveTo(x, y);
          for (let k = 0; k < 6; k++) { x += (Math.random() - 0.5) * 30; y += Math.random() * 18; dc.lineTo(x, y); }
          dc.stroke();
        }
        // The long scratch drifts slowly, the way one does down a reel.
        scratchX += (Math.random() - 0.5) * 0.01;
        dc.strokeStyle = `rgba(250, 248, 240, ${0.25 + Math.random() * 0.35})`;
        dc.beginPath();
        dc.moveTo(scratchX * w, 0);
        dc.lineTo(scratchX * w + (Math.random() - 0.5) * 3, h);
        dc.stroke();
        leader.style.setProperty("--flick", (0.9 + Math.random() * 0.12).toFixed(3));
      };
      requestAnimationFrame(paint);
      let timer = null;
      leader.classList.add("is-on");
      document.documentElement.classList.add("has-leader");
      const done = (withSound) => {
        clearInterval(timer);
        removeEventListener("wheel", skip);
        removeEventListener("touchmove", skip);
        document.documentElement.classList.remove("has-leader");
        // The hand-off: a black frame after the 2, then the reel comes up in
        // the same gate. The sprockets run off and the dirt thins out on the
        // picture, so it reads as one strip of film, not a page loading.
        leader.classList.add(withSound ? "is-handoff" : "is-done");
        setTimeout(() => leader.remove(), withSound ? 2600 : 500);
        if (withSound && sfx.on) {
          setReelSound(true);
          if (reelEl) { reelEl.currentTime = 0; reelEl.play().catch(() => {}); }
        }
      };
      const skip = () => done(false);
      // 800 ms a number: the real leader runs a second per number, trimmed
      // so the reel isn't kept waiting more than 2.4 s.
      const roll = () => {
        sfx.wake();
        leader.classList.add("is-rolling");
        let k = 3;
        const tick = () => {
          num.textContent = String(k);
          leader.classList.remove("is-tick");
          void leader.offsetWidth;
          leader.classList.add("is-tick");
          sfx.beep(k);
        };
        sfx.clatter(2.6);
        tick();
        timer = setInterval(() => {
          k -= 1;
          if (k === 0) return done(true);
          tick();
        }, 800);
      };
      // The ticket: a new serial each visit; a click tears the stub off and
      // the countdown starts once the halves have cleared.
      const ticket = leader.querySelector(".admit");
      const serial = String(Math.floor(100000 + Math.random() * 899999));
      ticket.querySelectorAll(".admit__serial").forEach((x) => { x.textContent = serial; });
      ticket.addEventListener("click", () => {
        sfx.wake();
        sfx.rip();
        ticket.classList.add("is-torn");
        setTimeout(roll, reduced ? 0 : 650);
      }, { once: true });
      leader.querySelector(".leader__roll").focus({ preventScroll: true });
      addEventListener("wheel", skip, { once: true, passive: true });
      addEventListener("touchmove", skip, { once: true, passive: true });
      addEventListener("keydown", (e) => {
        if (e.key === "Escape" || e.key === "ArrowDown" || e.key === "PageDown") skip();
      }, { once: true });
    }
  }
  // The masthead's projector button: sound on or off from anywhere.
  const mastSound = document.querySelector(".mast__sound");
  if (mastSound) {
    const show = () => mastSound.setAttribute("aria-pressed", String(sfx.on));
    show();
    mastSound.addEventListener("click", () => {
      sfx.set(!sfx.on);
      sfx.wake();
      setReelSound(sfx.on);
      if (sfx.on) sfx.tick();
      show();
    });
  }
  // The score's set pieces: a click at every splice, and the motif once at
  // each part, each on its own instrument.
  if (window.score) {
    document.querySelectorAll(".splice").forEach((el) => window.score.watch(el, "splice"));
    const parts = [...document.querySelectorAll(".intertitle")];
    const voices = ["motif:brass", "motif:celesta", "motif:piano"];
    parts.forEach((el, i) => { if (voices[i]) window.score.watch(el, voices[i]); });
    if (document.querySelector(".callsheet")) window.score.watch(".callsheet", "motif:guitar");
    if (document.querySelector(".monitor")) window.score.watch(".monitor", "crt");
  }
  // Sound on by default: the first click or key anywhere turns the reel up,
  // unless the visitor switched sound off.
  const firstGesture = (e) => {
    if (e.target.closest && e.target.closest(".sound, .leader")) return;
    sfx.wake();
    if (sfx.on && reelEl && soundBtn && soundBtn.getAttribute("aria-pressed") !== "true") setReelSound(true);
  };
  addEventListener("pointerdown", firstGesture, { once: true });
  addEventListener("keydown", firstGesture, { once: true });

  // Same-page anchors glide instead of jumping.
  document.addEventListener("click", (e) => {
    const a = e.target.closest('a[href^="#"]');
    if (!a || a.dataset.step !== undefined) return;
    const target = document.querySelector(a.getAttribute("href"));
    if (!target) return;
    e.preventDefault();
    glide(target.getBoundingClientRect().top + scrollY - 56);
    history.replaceState(null, "", a.getAttribute("href"));
  });

  // Reel: muted loop, one toggle for sound, pauses when off screen.
  const reel = document.querySelector("#reel");
  const sound = document.querySelector(".sound");
  if (reel && sound) {
    sound.addEventListener("click", () => {
      const on = sound.getAttribute("aria-pressed") !== "true";
      sfx.set(on);
      setReelSound(on);
      if (on) reel.play().catch(() => {});
    });
    new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) reel.play().catch(() => {});
        else reel.pause();
      },
      { threshold: 0.2 },
    ).observe(reel);
  }

  // Now Showing: the programme picks which loop and which panel are on.
  const screen = document.querySelector(".screen");
  if (screen) {
    const videos = [...screen.querySelectorAll("video")];
    const panels = [...document.querySelectorAll(".now .panel")];
    const items = [...document.querySelectorAll(".programme a")];
    let current = 0;
    let visible = false;

    const select = (i) => {
      if (i === current) return;
      videos[current].pause();
      videos.forEach((v, k) => v.classList.toggle("is-on", k === i));
      panels.forEach((p, k) => {
        p.classList.toggle("is-on", k === i);
        p.setAttribute("aria-hidden", String(k !== i));
        p.querySelector("a").tabIndex = k === i ? 0 : -1;
      });
      items.forEach((a, k) => a.setAttribute("aria-current", String(k === i)));
      current = i;
      if (visible) videos[i].play().catch(() => {});
      screen.href = items[i].getAttribute("href");
      screen.setAttribute(
        "aria-label",
        `Watch ${items[i].querySelector(".t").textContent}`,
      );
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
    videos.forEach((v, k) =>
      v.addEventListener("canplay", () => {
        if (visible && k === current && v.paused) v.play().catch(() => {});
      }),
    );

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
  }

  // Opening: the reel shrinks into a framed screen over the first scroll.
  const opening = document.querySelector(".opening");
  const cue = document.querySelector(".cue");
  // Pinned scenes (featured films, About): scroll position picks the chapter.
  const scenes = [...document.querySelectorAll(".scene")].map((scene) => {
    const layers = [...scene.querySelectorAll(".scene__bg > *")];
    const lines = [...scene.querySelectorAll(".line")];
    const ticks = [...scene.querySelectorAll(".scene__ticks i")];
    const tabs = [...scene.querySelectorAll(".scene__nav a")];
    const steps = lines.length;
    const isVideo = layers[0] && layers[0].tagName === "VIDEO";
    const st = { at: 0, live: false };
    const span = () => scene.offsetHeight - innerHeight;
    const top = () => scene.getBoundingClientRect().top + scrollY;
    const playCurrent = () => {
      if (!isVideo) return;
      layers.forEach((v, k) => {
        if (st.live && k === st.at) {
          if (v.preload !== "auto") v.preload = "auto";
          v.play().catch(() => {});
        } else v.pause();
      });
    };
    const set = (i) => {
      if (i === st.at) return;
      st.at = i;
      layers.forEach((x, k) => x.classList.toggle("is-on", k === i));
      lines.forEach((x, k) => {
        x.classList.toggle("is-on", k === i);
        x.setAttribute("aria-hidden", String(k !== i));
        const link = x.querySelector("a");
        if (link) link.tabIndex = k === i ? 0 : -1;
      });
      ticks.forEach((x, k) => x.classList.toggle("is-on", k === i));
      scene.dispatchEvent(new CustomEvent("chapter", { detail: i }));
      tabs.forEach((x, k) => x.setAttribute("aria-current", String(k === i)));
      // Warm the next loop so it is ready when the reader gets there.
      if (isVideo && layers[i + 1]) layers[i + 1].preload = "auto";
      playCurrent();
    };
    new IntersectionObserver(([entry]) => {
      st.live = entry.isIntersecting;
      playCurrent();
    }).observe(scene);
    if (isVideo) layers.forEach((v, k) => v.addEventListener("canplay", () => {
      if (st.live && k === st.at && v.paused) v.play().catch(() => {});
    }));
    tabs.forEach((t) => t.addEventListener("click", (e) => {
      e.preventDefault();
      glide(top() + span() * ((Number(t.dataset.step) + 0.5) / steps));
    }));
    return () => {
      const p = (scrollY - top()) / span();
      set(Math.max(0, Math.min(steps - 1, Math.floor(p * steps))));
    };
  });

  // Now Showing: a theater marquee. Black letters on the backlit board,
  // each one flips over to spell the film that's on.
  const marquee = document.querySelector(".marquee");
  if (marquee) {
    const scene = marquee.closest(".scene");
    const board = marquee.querySelector(".marquee__board");
    const bottom = marquee.querySelector(".marquee__bottom");
    const titles = [...scene.querySelectorAll(".card__title")].map((x) => x.textContent);
    const metas = [...scene.querySelectorAll(".card__meta")].map((x) => x.textContent);
    const spell = (i, animate) => {
      board.replaceChildren();
      const words = titles[i].toUpperCase().split(" ");
      // 14 ms a letter keeps the longest title (25 letters) under 400 ms.
      let k = 0;
      words.forEach((w) => {
        const word = document.createElement("span");
        word.className = "marquee__word";
        [...w].forEach((ch) => {
          const t = document.createElement("span");
          t.className = "tile";
          t.textContent = ch;
          if (animate && !reduced) t.style.animationDelay = `${k * 14}ms`;
          else t.classList.add("is-still");
          k += 1;
          word.appendChild(t);
        });
        board.appendChild(word);
      });
      bottom.textContent = metas[i];
    };
    spell(0, false);
    scene.addEventListener("chapter", (e) => { spell(e.detail, true); sfx.flap(titles[e.detail].length); });
  }

  // Photography: the light table. Scrolling pans across every slide; the
  // loupe magnifies whatever's under it (the cursor on desktop, the center
  // on a phone).
  const table = document.querySelector(".lighttable");
  let tableUpdate = null;
  if (table) {
    const pin = table.querySelector(".lighttable__pin");
    const surface = table.querySelector(".lighttable__surface");
    const loupe = table.querySelector(".loupe");
    const view = loupe.querySelector(".loupe__view");
    view.appendChild(surface.cloneNode(true));
    const copy = view.firstElementChild;
    copy.querySelectorAll("button").forEach((b) => b.setAttribute("tabindex", "-1"));
    copy.querySelectorAll("img").forEach((im) => { im.loading = "eager"; im.src = im.getAttribute("src"); });
    const head = table.querySelector(".lighttable__head");
    let tx = 0;
    let ty = 0;
    let lx = innerWidth / 2;
    let ly = innerHeight * 0.58;
    // 2x is a real loupe's working magnification for 35mm slides on a table.
    const MAG = 2;
    const place = () => {
      const R = loupe.clientWidth / 2;
      loupe.style.transform = `translate(${lx - R}px, ${ly - R}px)`;
      const sx = lx - tx;
      const sy = ly - ty - surface.offsetTop;
      copy.style.transform = `translate(${R - sx * MAG}px, ${R - sy * MAG}px) scale(${MAG})`;
    };
    tableUpdate = () => {
      const top = table.getBoundingClientRect().top + scrollY;
      const p = Math.max(0, Math.min(1, (scrollY - top) / (table.offsetHeight - innerHeight)));
      const W = surface.scrollWidth - pin.clientWidth;
      const H = surface.scrollHeight - (pin.clientHeight - surface.offsetTop);
      // An S across the table, the way you'd slide a loupe over it.
      tx = -Math.max(0, W) * (0.5 - 0.5 * Math.cos(p * Math.PI * 2)) * 0.9 - Math.max(0, W) * 0.05;
      ty = -Math.max(0, H) * p;
      surface.style.transform = `translate(${tx}px, ${ty}px)`;
      head.style.opacity = String(Math.max(0, 1 - p * 7));
      place();
    };
    if (fine) pin.addEventListener("mousemove", (e) => { lx = e.clientX; ly = e.clientY; place(); });
    addEventListener("resize", () => tableUpdate());
    addEventListener("scroll", () => requestAnimationFrame(tableUpdate), { passive: true });
    tableUpdate();
  }

  // All Films: a Premiere-style edit. Scrolling drags the timeline under a
  // fixed playhead. Every cut carries a transition that renders live in the
  // Program monitor as the playhead crosses it, and Effect Controls follow.
  const edit = document.querySelector(".edit");
  let scrub = null;
  if (edit) {
    const strip = edit.querySelector(".timeline__strip");
    const win = edit.querySelector(".timeline__window");
    const ruler = edit.querySelector(".ruler");
    const lane = edit.querySelector(".fxlane");
    const clips = [...edit.querySelectorAll(".clip")];
    const $ = (sel) => edit.querySelector(sel);
    const A = $(".monitor__a");
    const B = $(".monitor__b");
    const aImg = A.querySelector("img");
    const bImg = B.querySelector("img");
    const tc = $(".monitor__tc");
    const tc2 = $(".monitor__tc2");
    const tc3 = $(".monitor__tc3");
    const luClip = $(".lu__clip");
    const luTemp = $(".lu__temp");
    const luExp = $(".lu__exp");
    const trLabel = $(".monitor__trlabel");
    const title = $(".monitor__title");
    const meta = $(".monitor__meta");
    const open = $(".monitor__open");
    const fx = {
      clip: $(".fxc__clip"), pos: $(".fxc__pos"), scale: $(".fxc__scale"), op: $(".fxc__op"),
      name: $(".fxc__trname"), fill: $(".fxc__fill"), temp: $(".fxc__temp"), exp: $(".fxc__exp"),
    };
    const KINDS = ["Cross Dissolve", "Dip to Black", "Push", "Iris Round", "Film Dissolve", "Cut"];
    let px = 30;
    let half = 40;
    let video = null;
    let cur = -1;
    const layout = () => {
      px = innerWidth < 700 ? 16 : 30;
      clips.forEach((c) => { c.style.width = `${Math.max(innerWidth < 700 ? 84 : 120, Number(c.dataset.min) * px)}px`; });
      // A transition straddles each cut, 1.6 s of screen time a side.
      half = innerWidth < 700 ? 34 : 56;
      ruler.replaceChildren();
      lane.replaceChildren();
      clips.forEach((c) => c.querySelector(".clip__t") && c.querySelector(".clip__t").remove());
      let last = "";
      clips.forEach((c, i) => {
        if (c.dataset.year !== last) {
          last = c.dataset.year;
          const tchip = document.createElement("span");
          tchip.className = "clip__t";
          tchip.textContent = last;
          c.prepend(tchip);
          const m = document.createElement("span");
          m.className = "ruler__year";
          m.textContent = last;
          m.style.left = `${c.offsetLeft}px`;
          ruler.appendChild(m);
        }
        if (i < clips.length - 1) {
          const t = document.createElement("span");
          t.className = "fxlane__tr";
          t.textContent = KINDS[i % KINDS.length];
          // Drawn the way an NLE draws it: a narrow hatched block on the cut.
          t.style.left = `${c.offsetLeft + c.offsetWidth - 7}px`;
          t.style.width = "14px";
          lane.appendChild(t);
        }
      });
      // Ruler timecodes every 5 minutes of Parker's runtime.
      for (let m = 0; m * px < strip.scrollWidth; m += 5) {
        const t = document.createElement("span");
        t.className = "ruler__tc";
        t.textContent = `00:${String(m).padStart(2, "0")}:00:00`;
        t.style.left = `${m * px}px`;
        ruler.appendChild(t);
      }
      edit.style.height = `${strip.scrollWidth + innerHeight * 1.2}px`;
    };
    let lastK = -1;
    const setClip = (i) => {
      if (i === cur) return;
      if (cur >= 0) sfx.tick();
      cur = i;
      const c = clips[i];
      clips.forEach((x, k) => x.classList.toggle("is-on", k === i));
      aImg.src = c.dataset.still;
      title.textContent = c.dataset.title;
      meta.textContent = c.dataset.meta;
      open.href = c.getAttribute("href");
      fx.clip.textContent = c.dataset.title;
      if (luClip) luClip.textContent = c.dataset.title;
      // Each clip carries its own grade, the way a colorist leaves them.
      fx.temp.textContent = (((i * 37) % 21) - 10).toFixed(1);
      fx.exp.textContent = ((((i * 13) % 9) - 4) / 10).toFixed(1);
      if (luTemp) { luTemp.textContent = fx.temp.textContent; luTemp.previousElementSibling.firstElementChild.style.left = `${50 + Number(fx.temp.textContent) * 2.5}%`; }
      if (luExp) { luExp.textContent = fx.exp.textContent; luExp.previousElementSibling.firstElementChild.style.left = `${50 + Number(fx.exp.textContent) * 40}%`; }
      if (video) { video.remove(); video = null; }
      if (c.dataset.loop) {
        video = document.createElement("video");
        Object.assign(video, { muted: true, loop: true, playsInline: true, autoplay: true, src: c.dataset.loop });
        A.appendChild(video);
        video.play().catch(() => {});
      }
    };
    const reset = () => {
      A.style.cssText = "";
      B.style.cssText = "";
      B.classList.remove("is-on");
    };
    // t runs 0 to 1 across the transition; the first half is the outgoing clip.
    const render = (kind, t) => {
      reset();
      B.classList.add("is-on");
      let op = 100;
      let x = 960;
      if (kind === "Cross Dissolve") { B.style.opacity = t; op = (1 - t) * 100; }
      if (kind === "Film Dissolve") { B.style.opacity = t ** 1.8; A.style.filter = `brightness(${1 + t * 0.35})`; op = (1 - t ** 1.8) * 100; }
      if (kind === "Dip to Black") { A.style.opacity = Math.max(0, 1 - t * 2); B.style.opacity = Math.max(0, t * 2 - 1); op = Math.abs(1 - t * 2) * 100; }
      if (kind === "Push") { A.style.transform = `translateX(${-t * 100}%)`; B.style.transform = `translateX(${(1 - t) * 100}%)`; x = 960 - t * 1920; }
      if (kind === "Iris Round") { B.style.clipPath = `circle(${t * 75}% at 50% 50%)`; }
      if (kind === "Cut") { B.style.opacity = t < 0.5 ? 0 : 1; op = t < 0.5 ? 100 : 0; }
      fx.op.textContent = `${op.toFixed(1)} %`;
      fx.pos.innerHTML = `${x.toFixed(1)} &nbsp;540.0`;
      fx.name.textContent = kind;
      fx.fill.style.width = `${t * 100}%`;
      trLabel.textContent = kind;
      trLabel.classList.add("is-on");
    };
    const pad2 = (v) => String(Math.floor(v)).padStart(2, "0");
    scrub = () => {
      const top = edit.getBoundingClientRect().top + scrollY;
      const span = edit.offsetHeight - innerHeight;
      const p = Math.max(0, Math.min(1, (scrollY - top) / span));
      const total = strip.scrollWidth;
      const xh = p * (total - 1);
      strip.style.transform = `translateX(${win.clientWidth / 2 - xh}px)`;
      let i = clips.findIndex((c) => xh >= c.offsetLeft && xh < c.offsetLeft + c.offsetWidth);
      if (i < 0) i = xh <= 0 ? 0 : clips.length - 1;
      // Inside a transition, the outgoing clip stays on A and the next on B.
      const c = clips[i];
      const end = c.offsetLeft + c.offsetWidth;
      let k = -1;
      let t = 0;
      if (i < clips.length - 1 && xh > end - half) { k = i; t = (xh - (end - half)) / (half * 2); }
      else if (i > 0 && xh < c.offsetLeft + half) { k = i - 1; t = (xh - (c.offsetLeft - half)) / (half * 2); }
      if (k >= 0 && k !== lastK && /Push|Iris/.test(KINDS[k % KINDS.length])) sfx.whoosh();
      lastK = k;
      if (k >= 0 && !reduced) {
        setClip(k);
        if (bImg.dataset.for !== String(k + 1)) { bImg.src = clips[k + 1].dataset.still; bImg.dataset.for = String(k + 1); }
        render(KINDS[k % KINDS.length], Math.max(0, Math.min(1, t)));
        if (t > 0.5) { title.textContent = clips[k + 1].dataset.title; meta.textContent = clips[k + 1].dataset.meta; open.href = clips[k + 1].getAttribute("href"); }
      } else {
        setClip(i);
        reset();
        fx.op.textContent = "100.0 %";
        fx.pos.innerHTML = "960.0 &nbsp;540.0";
        fx.name.textContent = "Lumetri Color";
        fx.fill.style.width = "0";
        trLabel.classList.remove("is-on");
      }
      fx.scale.textContent = (100 + Math.sin(xh / 90) * 4).toFixed(1);
      // Timecode is real: Parker's runtimes, added up to the playhead.
      const mins = xh / px;
      tc.textContent = `${pad2(mins / 60)}:${pad2(mins % 60)}:${pad2((mins * 60) % 60)}:${pad2((mins * 1440) % 24)}`;
      if (tc2) tc2.textContent = tc.textContent;
      if (tc3) tc3.textContent = tc.textContent;
    };
    layout();
    addEventListener("resize", () => { layout(); scrub(); });
  }

  // Cinematographer: one take. It opens on Parker at the camera and pushes
  // past his shoulder into its monitor; then the camera slides along a strip
  // of his frames, stopping on each while one setting moves live.
  const cam = document.querySelector(".cam");
  let camUpdate = null;
  if (cam) {
    const shots = [...document.querySelectorAll(".cam__shots li")].map((li) => ({ ...li.dataset }));
    const frame = cam.querySelector(".cam__frame");
    const strip = cam.querySelector(".cam__strip");
    const imgs = [...strip.querySelectorAll("img")];
    const tint = cam.querySelector(".cam__tint");
    const what = cam.querySelector(".cam__what");
    const val = cam.querySelector(".cam__val");
    const why = cam.querySelector(".cam__why");
    const mark = cam.querySelector(".cam__mark");
    const dist = cam.querySelector(".cam__dist");
    const hud = (k) => cam.querySelector(`[data-k="${k}"]`);
    const cap = document.querySelector(".lens .lens__title");
    const capMeta = document.querySelector(".lens .lens__meta");
    const NAMES = { focus: "Pulling focus", nd: "Adding ND", iris: "Stopping down", wb: "White balance", zoom: "Zooming out" };
    const STOPS = [1.4, 2, 2.8, 4, 5.6, 8];
    // The first 16% of the scroll is the push into the monitor.
    const POV = 0;
    let cur = -1;
    let lastE = 0;
    let lastServo = 0;
    let rolled = false;
    const ease = (x) => (x < 0.5 ? 4 * x * x * x : 1 - (-2 * x + 2) ** 3 / 2);
    const clamp = (x) => Math.max(0, Math.min(1, x));
    camUpdate = () => {
      const top = cam.getBoundingClientRect().top + scrollY;
      const p = Math.max(0, Math.min(0.9999, (scrollY - top) / (cam.offsetHeight - innerHeight)));
      // The push: the photo scales in on the camera's top monitor and gives
      // way to the monitor itself.
      const k = 1;
      const q = clamp((p - POV) / (1 - POV));
      const i = Math.min(shots.length - 1, Math.floor(q * shots.length));
      const u = q * shots.length - i;
      // Hold on the frame for the first 75% of its stretch, then slide on.
      const slide = i < shots.length - 1 ? ease(clamp((u - 0.75) / 0.25)) : 0;
      strip.style.transform = `translateX(${(-(i + slide) * 100).toFixed(2)}%)`;
      const sh = shots[i];
      if (i !== cur) {
        cur = i;
        what.textContent = NAMES[sh.kind];
        why.textContent = sh.why;
        cap.textContent = sh.title;
        cap.href = sh.href;
        capMeta.textContent = `${sh.year} \u00b7 Cinematography by Parker Manley`;
        cam.dataset.kind = sh.kind;
        hud("wb").textContent = "5600K"; hud("iris").textContent = "T2.8"; hud("nd").textContent = "ND Clear"; hud("zoom").textContent = "35 mm";
        imgs.forEach((im) => { im.style.filter = ""; im.style.transform = ""; });
      }
      const e = reduced ? 1 : ease(clamp((u - 0.08) / 0.6));
      const from = Number(sh.from);
      const to = Number(sh.to);
      const v = from + (to - from) * e;
      const img = imgs[i];
      let filter = "";
      let scale = 1;
      tint.style.opacity = "0";
      if (sh.kind === "focus") {
        filter = `blur(${(9 * (1 - e)).toFixed(2)}px)`;
        val.textContent = `${v.toFixed(1)} m`;
        dist.textContent = `${v.toFixed(1)} m`;
        mark.style.left = `${(Math.log(v / 0.3) / Math.log(30)) * 100}%`;
      } else if (sh.kind === "nd") {
        filter = `brightness(${(1 + 1.1 * (1 - e)).toFixed(2)}) contrast(${(1 - 0.35 * (1 - e)).toFixed(2)})`;
        val.textContent = `ND ${v.toFixed(1)}`;
        hud("nd").textContent = v < 0.15 ? "ND Clear" : `ND ${v.toFixed(1)}`;
      } else if (sh.kind === "iris") {
        const stop = STOPS.reduce((a2, b2) => (Math.abs(b2 - v) < Math.abs(a2 - v) ? b2 : a2));
        filter = `brightness(${(1.75 - 0.75 * e).toFixed(2)}) contrast(${(0.75 + 0.25 * e).toFixed(2)})`;
        val.textContent = `T${stop}`;
        hud("iris").textContent = `T${stop}`;
      } else if (sh.kind === "wb") {
        tint.style.opacity = (0.55 * (1 - e) * (1 - slide)).toFixed(2);
        filter = `saturate(${(0.7 + 0.4 * e).toFixed(2)})`;
        val.textContent = `${Math.round(v / 50) * 50}K`;
        hud("wb").textContent = `${Math.round(v / 50) * 50}K`;
      } else if (sh.kind === "zoom") {
        scale = 1 + 0.9 * (1 - e);
        val.textContent = `${Math.round(v)} mm`;
        hud("zoom").textContent = `${Math.round(v)} mm`;
      }
      img.style.filter = filter;
      img.style.transform = `scale(${scale.toFixed(3)})`;
      frame.classList.toggle("is-adjusting", e > 0 && e < 1);
      const r = cam.getBoundingClientRect();
      const inView = r.top <= 0 && r.bottom >= innerHeight;
      if (inView && k >= 1 && !rolled) { rolled = true; sfx.rec(); }
      if (!inView) rolled = false;
      if (inView && /focus|iris|zoom/.test(sh.kind) && Math.abs(e - lastE) > 0.01 && performance.now() - lastServo > 70) {
        lastServo = performance.now();
        sfx.servo();
      }
      lastE = e;
    };
    addEventListener("resize", () => camUpdate());
  }

  // Director: the festival circuit. Laurels stamp onto the poster as you
  // scroll, and the count runs up with them.
  const circ = document.querySelector(".circuit");
  let circUpdate = null;
  if (circ) {
    const laurels = [...circ.querySelectorAll(".laurel")];
    const n = circ.querySelector(".circuit__n");
    let shown = -1;
    circUpdate = () => {
      const top = circ.getBoundingClientRect().top + scrollY;
      const p = Math.max(0, Math.min(1, (scrollY - top) / (circ.offsetHeight - innerHeight)));
      const k = reduced ? laurels.length : Math.min(laurels.length, Math.floor(p * 1.25 * (laurels.length + 1)));
      if (k === shown) return;
      if (k > shown && shown >= 0) sfx.stamp();
      shown = k;
      laurels.forEach((l, i) => l.classList.toggle("is-in", i < k));
      n.textContent = String(laurels.slice(0, k).filter((l) => l.querySelector("small").textContent === "Official Selection").length);
    };
  }

  // End card: an iris-out. The black closes in a circle on Parker and the
  // camera, then the card lands beside him.
  const iris = document.querySelector(".irisout");
  let irisUpdate = null;
  if (iris) {
    irisUpdate = () => {
      const top = iris.getBoundingClientRect().top + scrollY;
      const p = Math.max(0, Math.min(1, (scrollY - top) / (iris.offsetHeight - innerHeight)));
      const e = reduced ? 1 : 1 - (1 - Math.min(1, p / 0.7)) ** 3;
      iris.style.setProperty("--r", `${(140 - e * (140 - (innerWidth < 700 ? 30 : 22))).toFixed(2)}vmax`);
      if (p > 0.55 && window.score) window.score.motif("strings");
      const closed = e > 0.92;
      if (closed && !iris.classList.contains("is-closed")) sfx.runout();
      iris.classList.toggle("is-closed", closed);
    };
  }

  // Viewfinder: the timecode runs at 24 frames a second while it's on screen.
  const vfTc = document.querySelector(".vf__tc");
  if (vfTc) {
    let t0 = 0;
    let raf = 0;
    const p2 = (x) => String(Math.floor(x)).padStart(2, "0");
    const run = (t) => {
      if (!t0) t0 = t;
      const s = (t - t0) / 1000;
      vfTc.textContent = `00:${p2(s / 60)}:${p2(s % 60)}:${p2((s * 24) % 24)}`;
      raf = requestAnimationFrame(run);
    };
    new IntersectionObserver(([entry]) => {
      cancelAnimationFrame(raf);
      if (entry.isIntersecting && !reduced) raf = requestAnimationFrame(run);
    }).observe(vfTc.closest(".cam") || vfTc.closest(".scene"));
  }

  // Now Showing: one continuous dolly through nine theaters. Each screen sits
  // deeper than the last; the camera pushes through one into the next.
  const filmsScene = document.querySelector(".scene--films");
  let hall = null;
  if (filmsScene) {
    const screens = [...filmsScene.querySelectorAll(".scene__bg video")];
    // 1600px between theaters: at 900px perspective the next screen sits at
    // a third of the frame, small enough to read as the next room.
    const GAP = 1600;
    hall = () => {
      const top = filmsScene.getBoundingClientRect().top + scrollY;
      const p = Math.max(0, Math.min(1, (scrollY - top) / (filmsScene.offsetHeight - innerHeight)));
      const cam = p * (screens.length - 0.5) * GAP;
      screens.forEach((v, i) => {
        const z = cam - i * GAP;
        if (z > 400 || z < -GAP * 2.2) { v.style.visibility = "hidden"; return; }
        v.style.visibility = "visible";
        v.style.transform = `translateZ(${z.toFixed(1)}px)`;
        v.style.opacity = z > 0 ? Math.max(0, 1 - z / 300).toFixed(3) : "1";
      });
    };
  }

  let queued = false;
  const onScroll = () => {
    queued = false;
    // The header stays off the picture while the reel plays and comes in
    // once the reel is behind you.
    if (opening) document.documentElement.classList.toggle("at-opening", scrollY < opening.offsetHeight - innerHeight * 0.6);
    if (opening) {
      const p = Math.max(0, Math.min(1, scrollY / (opening.offsetHeight - innerHeight)));
      opening.style.setProperty("--p", reduced ? 0 : p.toFixed(3));
      // Cue marks: the projectionist's dots, top right, near the reel change.
      if (!reduced && cue) cue.classList.toggle("is-on", p > 0.82 && p < 0.97 && Math.floor(p * 60) % 3 !== 0);
    }
    scenes.forEach((update) => update());
    if (hall) hall();
    if (scrub) scrub();
    if (camUpdate) camUpdate();
    if (circUpdate) circUpdate();
    if (irisUpdate) irisUpdate();
  };
  addEventListener("scroll", () => {
    if (!queued) {
      queued = true;
      requestAnimationFrame(onScroll);
    }
  }, { passive: true });
  onScroll();

  // Film page: the YouTube player loads only when asked for.
  const player = document.querySelector(".player[data-yt], .player[data-drive]");
  if (player) {
    const btn = player.querySelector("button");
    btn.addEventListener("click", () => {
      if (window.score) window.score.duck(true);
      const f = document.createElement("iframe");
      f.src = player.dataset.yt
        ? `https://www.youtube-nocookie.com/embed/${player.dataset.yt}?autoplay=1&rel=0&modestbranding=1&playsinline=1`
        : `https://drive.google.com/file/d/${player.dataset.drive}/preview`;
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
      // Our own validation, in the page's voice, instead of the browser bubble.
      const bad = [...form.querySelectorAll("input[required], textarea[required]")].filter((f) => !f.checkValidity());
      form.querySelectorAll(".is-invalid").forEach((f) => f.classList.remove("is-invalid"));
      if (bad.length) {
        bad.forEach((f) => f.classList.add("is-invalid"));
        const email = bad.find((f) => f.type === "email" && f.value);
        status.dataset.state = "err";
        status.textContent = email ? "That email doesn't look right." : `Add your ${bad.map((f) => f.name).join(" and ")} so I can write back.`;
        bad[0].focus();
        return;
      }
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

  // Photography: a dark room, a carousel projector and the wall. Slide 0 is
  // the title; every change cuts to black, then the new slide flickers on.
  const room = document.querySelector(".room");
  if (room) {
    const wrap = document.querySelector(".photos");
    const shots = [...document.querySelectorAll(".lighttable__surface button")];
    const wall = room.querySelector(".wall");
    const img = wall.querySelector(".wall__img");
    const no = wall.querySelector(".wall__no");
    const tray = room.querySelector(".tray");
    const count = tray.querySelector(".tray__count");
    const slots = tray.querySelector(".tray__slots");
    const n = shots.length;
    const total = n + 1;
    const pad = (x) => String(x).padStart(2, "0");
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2 - Math.PI / 2;
      const cx = 60 + Math.cos(a) * 44;
      const cy = 60 + Math.sin(a) * 44;
      const r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      r.setAttribute("x", String(cx - 1.6));
      r.setAttribute("y", String(cy - 4));
      r.setAttribute("width", "3.2");
      r.setAttribute("height", "8");
      r.setAttribute("transform", `rotate(${(a * 180) / Math.PI + 90} ${cx} ${cy})`);
      slots.appendChild(r);
    }
    const rects = [...slots.children];
    let at = 0;
    let busy = false;
    const src = (i) => shots[i - 1].dataset.full;
    const warm = (i) => { if (i >= 1 && i <= n) { const im = new Image(); im.src = src(i); } };
    const paint = (i) => {
      at = (i + total) % total;
      wall.classList.toggle("is-title", at === 0);
      if (at > 0) img.src = src(at);
      no.textContent = at ? `No. ${pad(at)}` : "";
      count.textContent = at ? `${pad(at)} / ${pad(n)}` : "Title";
      tray.setAttribute("aria-valuenow", String(at));
      rects.forEach((r, k) => r.classList.toggle("is-on", k === at - 1));
      tray.querySelector(".tray__slots").style.transform = "";
      slots.setAttribute("transform", `rotate(${at ? -((at - 1) / n) * 360 : 0} 60 60)`);
      warm(at + 1);
    };
    // 110 ms of black is the gap a real carousel leaves while the next slide drops.
    const show = (i) => {
      const next = (i + total) % total;
      if (busy || next === at) return;
      if (reduced) { paint(next); return; }
      busy = true;
      if (at === 0 && window.score) { window.score.play("shutter"); window.score.play("flash", { at: 0.2 }); } else sfx.chk();
      room.classList.add("is-dark");
      setTimeout(() => {
        paint(next);
        const on = () => {
          room.classList.remove("is-dark");
          room.classList.remove("is-flick");
          void room.offsetWidth;
          room.classList.add("is-flick");
          busy = false;
        };
        if (next === 0 || img.complete) on();
        else { img.addEventListener("load", on, { once: true }); img.addEventListener("error", on, { once: true }); }
      }, 110);
    };
    paint(0);
    warm(1);
    room.querySelectorAll("[data-step]").forEach((b) =>
      b.addEventListener("click", () => show(at + Number(b.dataset.step))));
    wall.querySelector(".wall__hit--pv").addEventListener("click", () => show(at - 1));
    wall.querySelector(".wall__hit--nx").addEventListener("click", () => show(at + 1));
    tray.addEventListener("click", (e) => {
      const r = tray.querySelector("svg").getBoundingClientRect();
      const a = Math.atan2(e.clientY - (r.top + r.height / 2), e.clientX - (r.left + r.width / 2)) + Math.PI / 2;
      // The tray turns, so the angle is read relative to the slide on top.
      const k = Math.round(((((a / (Math.PI * 2)) % 1) + 1) % 1) * n);
      show(((Math.max(at, 1) - 1 + k) % n) + 1);
    });
    tray.addEventListener("keydown", (e) => {
      if (e.key === "ArrowUp") show(at + 1);
      if (e.key === "ArrowDown") show(at - 1);
    });
    let x0 = null;
    wall.addEventListener("touchstart", (e) => { x0 = e.touches[0].clientX; }, { passive: true });
    wall.addEventListener("touchend", (e) => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0;
      x0 = null;
      if (Math.abs(dx) > 40) show(at + (dx < 0 ? 1 : -1));
    });
    const setView = (v) => {
      wrap.dataset.view = v;
      scrollTo(0, 0);
    };
    document.querySelectorAll("[data-view]").forEach((b) => {
      if (b.classList.contains("photos")) return;
      b.addEventListener("click", () => setView(b.dataset.view));
    });
    shots.forEach((b, i) => b.addEventListener("click", () => {
      setView("projector");
      paint(i + 1);
    }));
    addEventListener("keydown", (e) => {
      if (wrap.dataset.view !== "projector" || e.target.closest("input, textarea")) return;
      if (e.key === "ArrowLeft") show(at - 1);
      if (e.key === "ArrowRight" || e.key === " ") { e.preventDefault(); show(at + 1); }
    });
  }

  // All Films: the year's screen shows whichever film the pointer is on.
  if (fine) {
    document.querySelectorAll(".yr").forEach((yr) => {
      const screen = yr.querySelector(".yr__screen");
      const still = screen.querySelector("img");
      const now = screen.querySelector(".yr__now");
      let video = null;
      yr.querySelectorAll(".bill").forEach((b) => b.addEventListener("mouseenter", () => {
        still.src = b.dataset.still;
        now.textContent = b.dataset.title;
        if (video) { video.remove(); video = null; }
        if (b.dataset.loop) {
          video = document.createElement("video");
          Object.assign(video, { muted: true, loop: true, playsInline: true, src: b.dataset.loop });
          video.addEventListener("loadeddata", () => { video && (video.currentTime = 0.5); });
          screen.insertBefore(video, now);
          video.play().catch(() => {});
        }
      }));
    });
  }

  // Slate: the sticks clap when the message goes.
  const slate = document.querySelector(".slate");
  if (slate) {
    slate.querySelector("form").addEventListener("submit", () => {
      slate.classList.remove("is-clap");
      void slate.offsetWidth;
      slate.classList.add("is-clap");
      sfx.clack();
    });
  }
})();
