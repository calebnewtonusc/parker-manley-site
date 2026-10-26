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
      // A pop on every number of the countdown: 3, 2, 1.
      beep() { play("pop2"); },
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
        removeEventListener("wheel", tear);
        removeEventListener("touchmove", tear);
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
      // Parker, 2026-10-26: scrolling tears the ticket and plays the leader
      // (it used to skip it). A click still works. Browsers don't count a
      // wheel turn as permission for sound, so a scroll-start plays the
      // countdown silent unless sound was already on.
      let torn = false;
      const tear = () => {
        if (torn) return;
        torn = true;
        sfx.wake();
        sfx.rip();
        ticket.classList.add("is-torn");
        setTimeout(roll, reduced ? 0 : 650);
      };
      ticket.addEventListener("click", tear, { once: true });
      leader.querySelector(".leader__roll").focus({ preventScroll: true });
      addEventListener("wheel", tear, { once: true, passive: true });
      addEventListener("touchmove", tear, { once: true, passive: true });
      addEventListener("keydown", (e) => {
        if (e.key === "Escape") skip();
        else if (e.key === "ArrowDown" || e.key === "PageDown" || e.key === " ") tear();
      });
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
    // The reel's music rides the scroll: it fades down over about two
    // seconds as the reel leaves and back up as you return, then pauses only
    // once it's silent. A hard cut here read as a mistake.
    let level = 1;
    let target = 1;
    let last = 0;
    let fading = 0;
    const FADE_S = 2.2;
    const step = (t) => {
      const dt = last ? (t - last) / 1000 : 0;
      last = t;
      const d = target - level;
      level += Math.sign(d) * Math.min(Math.abs(d), dt / FADE_S);
      try { reel.volume = level; } catch (err) { /* iOS keeps volume fixed */ }
      if (level <= 0.001 && target === 0) {
        // Silent, but it keeps rolling while it's on the camera's flip screen.
        const kn = document.querySelector(".knoll");
        const kr = kn && kn.getBoundingClientRect();
        if (!(kr && kr.top < innerHeight && kr.bottom > 0 && innerWidth >= 900)) reel.pause();
        fading = 0; last = 0; return;
      }
      if (Math.abs(target - level) < 0.001) { fading = 0; last = 0; return; }
      fading = requestAnimationFrame(step);
    };
    const thresholds = Array.from({ length: 11 }, (_, i) => i / 10);
    new IntersectionObserver(
      ([entry]) => {
        target = Math.min(1, entry.intersectionRatio / 0.6);
        if (target > 0 && reel.paused) reel.play().catch(() => {});
        if (!fading) fading = requestAnimationFrame(step);
      },
      { threshold: thresholds },
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

  // Now Showing: the marquee board is a picture of a real board, one per
  // film. It swaps on the same beat as the cut, with the letters' clatter.
  const marquee = document.querySelector(".marquee__img");
  if (marquee) {
    const slugs = marquee.dataset.slugs.split(" ");
    slugs.forEach((sl) => { const im = new Image(); im.src = `/media/titles/marquee-${sl}-900.webp`; });
    marquee.closest(".scene").addEventListener("chapter", (e) => {
      marquee.src = `/media/titles/marquee-${slugs[e.detail]}-900.webp`;
      sfx.flap(12);
    });
  }

  // All Films: a Premiere-style edit. Scrolling drags the timeline under a
  // fixed playhead. Every cut carries a transition that renders live in the
  // Program monitor as the playhead crosses it, and Effect Controls follow.
  const edit = document.querySelector(".edit");
  let scrub = null;
  if (edit) {
    const strip = edit.querySelector(".timeline__strip");
    const playhead = edit.querySelector(".playhead");
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
    // The cut the session drops a Cross Dissolve on, a little before the middle.
    const K = Math.floor(clips.length * 0.45);
    let cutline = null;
    let session = false;
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
          t.className = `fxlane__tr${i === K ? " is-pending" : ""}`;
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
      // The razor's cut line, drawn once, shown when the razor clicks.
      cutline = document.createElement("span");
      cutline.className = "cutline";
      lane.appendChild(cutline);
      session = innerWidth >= 900 && !reduced;
      // The session reads at about 90vh of scroll per action; the plain
      // playthrough keeps the old one-to-one length.
      edit.style.height = session ? `${innerHeight * 10.5}px` : `${strip.scrollWidth + innerHeight * 1.2}px`;
      // Overlap the camera's last screenful exactly, measured, so the edit
      // bay is already in place when the camera section lets go.
      const camEl = document.querySelector(".cam");
      edit.style.marginTop = "0px";
      if (session && camEl) {
        const camEnd = camEl.getBoundingClientRect().bottom + scrollY;
        const natural = edit.getBoundingClientRect().top + scrollY;
        edit.style.marginTop = `${(camEnd - innerHeight - natural).toFixed(0)}px`;
      }
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
    let dropped = false;
    const kindAt = (k) => (k === K ? (dropped ? "Cross Dissolve" : "Cut") : KINDS[k % KINDS.length]);
    const pad2 = (v) => String(Math.floor(v)).padStart(2, "0");

    // The editing session: one scripted pass by Parker's cursor, driven by
    // scroll so it plays forward and backward exactly.
    const pin = edit.querySelector(".fc");
    const cursor = document.createElement("div");
    cursor.className = "fc__cursor";
    cursor.innerHTML = '<svg viewBox="0 0 16 24" aria-hidden="true"><path d="M1 1v18.5l4.6-4.3 2.9 6.9 2.8-1.2-2.9-6.7H15z" fill="#fff" stroke="#000" stroke-width="1.2" stroke-linejoin="round"/></svg><span class="fc__ghost">Cross Dissolve</span>';
    pin.appendChild(cursor);
    const lerp = (a, b, t) => a + (b - a) * t;
    const ease = (t) => (t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2);
    const seg = (T, a, b) => Math.max(0, Math.min(1, (T - a) / (b - a)));
    const at = (el, fx = 0.5, fy = 0.5) => {
      const r = el.getBoundingClientRect();
      const q = pin.getBoundingClientRect();
      return { x: r.left - q.left + r.width * fx, y: r.top - q.top + r.height * fy };
    };
    const tl = (x) => {
      const r = win.getBoundingClientRect();
      const q = pin.getBoundingClientRect();
      const v1 = clips[0].querySelector(".clip__v").getBoundingClientRect();
      return { x: r.left - q.left + x, y: v1.top - q.top + v1.height * 0.6 };
    };
    const luTrack = luTemp ? luTemp.previousElementSibling : null;
    const luExpTrack = luExp ? luExp.previousElementSibling : null;
    const screen = $(".monitor__screen");
    const tools = [...edit.querySelectorAll(".fc__tools i")];
    const fxTab = edit.querySelector(".fc__lu .fc__tabs span:nth-child(2)");
    let lastT = 0;
    // Click moments in the session, so a click sounds once as you pass it.
    const CLICKS = [0.06, 0.39, 0.44, 0.475, 0.52, 0.6, 0.9];
    const script = (T) => {
      const c0 = clips[K - 1];
      const cK = clips[K];
      const cutKm1 = cK.offsetLeft;
      const cutK = cK.offsetLeft + cK.offsetWidth;
      const X0 = c0.offsetLeft + c0.offsetWidth * 0.2;
      const XA = cutKm1 + half + 24;
      const XR = cK.offsetLeft + cK.offsetWidth * 0.5;
      const XB = cutK + half + 30;
      const XEND = clips[Math.min(clips.length - 1, K + 3)].offsetLeft + 40;
      let xh = X0;
      if (T >= 0.06) xh = lerp(X0, XA, seg(T, 0.06, 0.22));
      if (T >= 0.28) xh = lerp(XA, XR, ease(seg(T, 0.28, 0.36)));
      if (T >= 0.6) xh = lerp(XR, XB, seg(T, 0.6, 0.7));
      if (T >= 0.9) xh = lerp(XB, XEND, seg(T, 0.9, 1));
      dropped = T >= 0.58;
      // Keep the playhead in view the way Premiere pages the timeline.
      const W = win.clientWidth;
      const off = Math.max(c0.offsetLeft - W * 0.08, xh - W * 0.78);
      strip.style.transform = `translateX(${-off}px)`;
      playhead.style.left = `${xh - off}px`;
      cutline.style.left = `${XR}px`;
      cutline.classList.toggle("is-on", T >= 0.44);
      lane.querySelector(".is-pending")?.classList.toggle("is-dropped", dropped);
      tools.forEach((t, i) => t.classList.toggle("is-on", i === (T >= 0.39 && T < 0.475 ? 1 : 0)));
      // The grade: Temperature, then Exposure, then a punch-in on Scale.
      const temp = 18 * ease(seg(T, 0.7, 0.76));
      const expo = 0.6 * ease(seg(T, 0.77, 0.82));
      const scl = 100 + 12 * ease(seg(T, 0.83, 0.88));
      if (luTemp) { luTemp.textContent = temp.toFixed(1); luTrack.firstElementChild.style.left = `${50 + temp * 2}%`; }
      if (luExp) { luExp.textContent = expo.toFixed(1); luExpTrack.firstElementChild.style.left = `${50 + expo * 40}%`; }
      fx.temp.textContent = temp.toFixed(1);
      fx.exp.textContent = expo.toFixed(1);
      screen.style.filter = `sepia(${(temp / 90).toFixed(3)}) saturate(${(1 + temp / 110).toFixed(3)}) brightness(${(1 + expo * 0.22).toFixed(3)})`;
      A.style.scale = String(scl / 100);
      fx.scale.textContent = scl.toFixed(1);
      // Where the cursor is, and what it's holding.
      const P = {
        play: () => at(edit.querySelector(".pm__play")),
        head: () => ({ x: tl(xh - off).x, y: at(playhead, 0.5, 0).y + 8 }),
        razor: () => at(tools[1]),
        select: () => at(tools[0]),
        clip: () => tl(XR - off),
        fx: () => at(fxTab),
        cut: () => tl(cutK - off),
        temp: () => at(luTrack.firstElementChild),
        expo: () => at(luExpTrack.firstElementChild),
        scale: () => at(fx.scale, 0.3, 0.5),
      };
      const off0 = { x: pin.clientWidth * 0.9, y: pin.clientHeight * 0.95 };
      const path = [
        [0, 0.05, () => off0, P.play], [0.05, 0.22, P.play, P.play], [0.22, 0.27, P.play, P.head], [0.27, 0.36, P.head, P.head],
        [0.36, 0.39, P.head, P.razor], [0.39, 0.43, P.razor, P.clip], [0.43, 0.47, P.clip, P.select], [0.47, 0.51, P.select, P.fx],
        [0.51, 0.58, P.fx, P.cut], [0.58, 0.6, P.cut, P.play], [0.6, 0.69, P.play, P.play], [0.69, 0.7, P.play, P.temp],
        [0.7, 0.76, P.temp, P.temp], [0.76, 0.77, P.temp, P.expo], [0.77, 0.82, P.expo, P.expo], [0.82, 0.83, P.expo, P.scale],
        [0.83, 0.88, P.scale, P.scale], [0.88, 0.9, P.scale, P.play], [0.9, 1.01, P.play, P.play],
      ];
      const step = path.find(([a, b]) => T >= a && T < b) || path[path.length - 1];
      const from = step[2]();
      const to = step[3]();
      const k = ease(seg(T, step[0], step[1]));
      let cx = lerp(from.x, to.x, k);
      const cy = lerp(from.y, to.y, k);
      if (step[0] === 0.83) cx += 60 * ease(seg(T, 0.83, 0.88));
      cursor.style.transform = `translate(${cx.toFixed(1)}px, ${cy.toFixed(1)}px)`;
      cursor.classList.toggle("is-down", CLICKS.some((c) => Math.abs(T - c) < 0.006) || (T > 0.27 && T < 0.36) || (T > 0.52 && T < 0.58) || (T > 0.7 && T < 0.76) || (T > 0.77 && T < 0.82) || (T > 0.83 && T < 0.88));
      cursor.classList.toggle("is-dragging", T > 0.52 && T < 0.58);
      cursor.classList.toggle("is-razor", T >= 0.39 && T < 0.475);
      const crossed = CLICKS.find((c) => (lastT < c && T >= c) || (lastT > c && T <= c));
      if (crossed !== undefined) sfx.tick();
      lastT = T;
      return xh;
    };

    const fcTop = edit.querySelector(".fc__top");
    const fcSide = [...edit.querySelectorAll(".fc__ec, .fc__lu, .fc__bottom, .fc__bar, .fc__note, .monitor .fc__tabs, .pm__row, .pm__transport")];
    const hand = document.createElement("img");
    hand.className = "fc__handoff";
    hand.alt = "";
    const lastCam = document.querySelector(".cam__strip img:last-child");
    if (lastCam) hand.src = lastCam.getAttribute("src");
    screen.appendChild(hand);
    // Hand-off in. Nothing is scaled. Premiere opens with the Program
    // monitor dragged edge to edge, every other panel collapsed to nothing,
    // and the camera's last frame fit to it exactly as the camera left it.
    // Then Parker's cursor drags the panels back in from the edges: the
    // menus down from the top, the left panel, the right panel, the
    // timeline up from the bottom. The picture shrinks with the viewer.
    const fcBottom = edit.querySelector(".fc__bottom");
    const mon = screen.closest(".monitor");
    const noteEl = edit.querySelector(".fc__note");
    const panes = (t, l, r, bt) => {
      pin.style.setProperty("--dt", t.toFixed(4));
      fcTop.style.gridTemplateColumns = `minmax(0, ${(0.9 * l + 0.0001).toFixed(4)}fr) minmax(0, 1.6fr) minmax(0, ${(0.75 * r + 0.0001).toFixed(4)}fr)`;
      const nh = noteEl ? noteEl.scrollHeight : 0;
      pin.style.gridTemplateRows = `${(28 * t).toFixed(1)}px ${(nh * t).toFixed(1)}px minmax(0, 1.05fr) minmax(0, ${(bt + 0.0001).toFixed(4)}fr)`;
      pin.style.gap = `${(3 * Math.min(l, r, t)).toFixed(2)}px`;
      pin.style.paddingInline = `${(3 * Math.min(l, r)).toFixed(2)}px`;
      fcTop.style.gap = `${(3 * Math.min(l, r)).toFixed(2)}px`;
    };
    const edgeAt = (which) => {
      const q = pin.getBoundingClientRect();
      const r = mon.getBoundingClientRect();
      if (which === "T") return { x: r.left - q.left + r.width * 0.5, y: r.top - q.top + 2 };
      if (which === "L") return { x: r.left - q.left + 2, y: r.top - q.top + r.height * 0.45 };
      if (which === "R") return { x: r.right - q.left - 2, y: r.top - q.top + r.height * 0.45 };
      return { x: r.left - q.left + r.width * 0.5, y: r.bottom - q.top - 2 };
    };
    const grow = (T) => {
      pin.style.transform = "";
      if (innerWidth < 900) { panes(1, 1, 1, 1); pin.classList.remove("is-handin"); hand.style.opacity = "0"; return false; }
      const d = (a2, b2) => ease(Math.max(0, Math.min(1, (T - a2) / (b2 - a2))));
      const dt = d(0.1, 0.26);
      const dl = d(0.34, 0.5);
      const dr = d(0.58, 0.74);
      const db = d(0.82, 0.96);
      panes(dt, dl, dr, db);
      pin.classList.toggle("is-handin", T < 1);
      hand.style.opacity = String(1 - Math.max(0, Math.min(1, (T - 0.96) / 0.04)));
      // The cursor: to an edge, press, drag, let go, next edge.
      const segs = [["T", 0.04, 0.1, 0.26], ["L", 0.28, 0.34, 0.5], ["R", 0.52, 0.58, 0.74], ["B", 0.76, 0.82, 0.96]];
      let pos = { x: pin.clientWidth * 0.62, y: pin.clientHeight * 0.66 };
      let prev = pos;
      let down = false;
      let axis = "y";
      for (const [w, t0, t1, t2] of segs) {
        const e2 = edgeAt(w);
        if (T < t0) { pos = prev; break; }
        if (T < t1) { const u = ease((T - t0) / (t1 - t0)); pos = { x: prev.x + (e2.x - prev.x) * u, y: prev.y + (e2.y - prev.y) * u }; break; }
        pos = e2;
        if (T < t2) { down = true; axis = w === "L" || w === "R" ? "x" : "y"; break; }
        prev = e2;
      }
      cursor.style.opacity = T < 0.03 ? "0" : "";
      cursor.style.transform = `translate(${pos.x.toFixed(1)}px, ${pos.y.toFixed(1)}px)`;
      cursor.classList.toggle("is-down", down);
      cursor.classList.toggle("is-resize-x", down && axis === "x");
      cursor.classList.toggle("is-resize-y", down && axis === "y");
      return T < 1;
    };
    scrub = () => {
      const top = edit.getBoundingClientRect().top + scrollY;
      const span = edit.offsetHeight - innerHeight;
      const p = Math.max(0, Math.min(1, (scrollY - top) / span));
      const total = strip.scrollWidth;
      let xh;
      if (session) {
        // Hand-off in: the same frame the camera ended on fills the program
        // monitor, and Premiere's panels grow in around it.
        // While the edit bay slides up under the camera's last screenful it
        // stays invisible; it appears only once it's pinned, already in the
        // exact frame the camera ended on.
        pin.style.visibility = edit.getBoundingClientRect().top > 0.5 ? "hidden" : "";
        const I = 0.22;
        if (p < I && !reduced) {
          xh = script(0);
          grow(p / I);
        } else {
          grow(1);
          // The session runs to 88%; the rest is Premiere leaving full
          // screen: the window shrinks onto the Mac and slides off it.
          // The exit fits the last screenful, the part the Mac sits under.
          const X0 = 1 - innerHeight / Math.max(1, edit.offsetHeight - innerHeight);
          xh = script(Math.min(1, (p - I) / (X0 - I)));
          if (p > X0 && !reduced) {
            const x = (p - X0) / (1 - X0);
            const sc = 1 - 0.3 * ease(Math.min(1, x / 0.45));
            const sl = ease(Math.max(0, (x - 0.5) / 0.5));
            pin.style.transformOrigin = "50% 50%";
            pin.style.transform = `translateX(${(-sl * 130).toFixed(2)}%) scale(${sc.toFixed(4)})`;
            pin.classList.add("is-windowed");
            pin.style.pointerEvents = x > 0.5 ? "none" : "";
          } else {
            pin.classList.remove("is-windowed");
            pin.style.pointerEvents = "";
          }
        }
      } else {
        xh = p * (total - 1);
        strip.style.transform = `translateX(${win.clientWidth / 2 - xh}px)`;
        playhead.style.left = "";
      }
      let i = clips.findIndex((c) => xh >= c.offsetLeft && xh < c.offsetLeft + c.offsetWidth);
      if (i < 0) i = xh <= 0 ? 0 : clips.length - 1;
      // Inside a transition, the outgoing clip stays on A and the next on B.
      const c = clips[i];
      const end = c.offsetLeft + c.offsetWidth;
      let k = -1;
      let t = 0;
      if (i < clips.length - 1 && xh > end - half) { k = i; t = (xh - (end - half)) / (half * 2); }
      else if (i > 0 && xh < c.offsetLeft + half) { k = i - 1; t = (xh - (c.offsetLeft - half)) / (half * 2); }
      if (k >= 0 && k !== lastK && /Push|Iris/.test(kindAt(k))) sfx.whoosh();
      lastK = k;
      if (k >= 0 && !reduced) {
        setClip(k);
        if (bImg.dataset.for !== String(k + 1)) { bImg.src = clips[k + 1].dataset.still; bImg.dataset.for = String(k + 1); }
        render(kindAt(k), Math.max(0, Math.min(1, t)));
        // Past the middle of a transition the incoming clip owns the monitor,
        // so the timeline's highlight moves with it; "Open film" and the
        // highlight never disagree (Parker, 2026-10-26).
        const shown = t > 0.5 ? k + 1 : k;
        clips.forEach((x, kk) => x.classList.toggle("is-on", kk === shown));
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
      if (!session) fx.scale.textContent = (100 + Math.sin(xh / 90) * 4).toFixed(1);
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
    let lastServo = -1;
    let rolled = false;
    const ease = (x) => (x < 0.5 ? 4 * x * x * x : 1 - (-2 * x + 2) ** 3 / 2);
    const clamp = (x) => Math.max(0, Math.min(1, x));
    const camFrame = cam.querySelector(".cam__frame");
    const camChrome = [...cam.querySelectorAll(".cam__hud, .vf, .cam__call, .cam__buttons, .pan__cap, .lens__title, .lens__meta, .cam__tally, .draft-mon, .draft-tag")];
    // The monitor is the 3D render's; the live screen is mapped onto its
    // glass in true perspective (a homography onto the exported quad). For
    // the hand-offs the same quad slides between the glass and the whole
    // screen, so nothing ever jumps.
    const rig = cam.querySelector(".rig__base");
    // The hall screen behind the rig shows the film being shot (Parker,
    // 2026-10-26). The still is mapped into the render's hall-screen quad and
    // masked by the render's own coverage, so the monitor still covers it.
    const hallFilm = document.createElement("div");
    hallFilm.className = "cam__hallfilm";
    hallFilm.innerHTML = '<div class="cam__hallfilm-in"><img alt=""></div>';
    if (rig) rig.after(hallFilm);
    const hallImg = hallFilm.querySelector("img");
    const hallIn = hallFilm.querySelector(".cam__hallfilm-in");
    cam.querySelector(".cam__screen")?.addEventListener("click", () => cam.querySelector(".cam__watch")?.click());
    const scr = cam.querySelector(".cam__screen");
    let RIG = null;
    fetch("/media/rig/monitor.json").then((r) => r.json()).then((j) => { RIG = j; handoff(lastZ); }).catch(() => {});
    const SW = 960, SH = 540;
    const homog = (q) => {
      // Maps the screen's own (0,0)-(SW,SH) rectangle onto quad q.
      const [[x0, y0], [x1, y1], [x2, y2], [x3, y3]] = q;
      const dx1 = x1 - x2, dx2 = x3 - x2, sx = x0 - x1 + x2 - x3;
      const dy1 = y1 - y2, dy2 = y3 - y2, sy = y0 - y1 + y2 - y3;
      const den = dx1 * dy2 - dx2 * dy1;
      const g = (sx * dy2 - dx2 * sy) / den;
      const h = (dx1 * sy - sx * dy1) / den;
      const A = x1 - x0 + g * x1, B = x3 - x0 + h * x3, C = x0;
      const D = y1 - y0 + g * y1, E = y3 - y0 + h * y3, F = y0;
      return `matrix3d(${A / SW},${D / SW},0,${g / SW},${B / SH},${E / SH},0,${h / SH},0,0,1,0,${C},${F},0,1)`;
    };
    let lastZ = 0;
    const handoff = (z) => {
      lastZ = z;
      if (!scr) return;
      if (innerWidth < 900 || !RIG || !rig) { scr.style.transform = ""; scr.classList.remove("is-mapped"); return; }
      scr.classList.add("is-mapped");
      const pin = rig.parentElement.getBoundingClientRect();
      const s = Math.max(pin.width / RIG.size[0], pin.height / RIG.size[1]);
      const ox = (pin.width - RIG.size[0] * s) / 2, oy = (pin.height - RIG.size[1] * s) / 2;
      const glass = RIG.screen.map(([x, y]) => [ox + x * s, oy + y * s]);
      let fw = pin.width, fh = fw * 9 / 16;
      if (fh > pin.height) { fh = pin.height; fw = fh * 16 / 9; }
      const fx = (pin.width - fw) / 2, fy = (pin.height - fh) / 2;
      const full = [[fx, fy], [fx + fw, fy], [fx + fw, fy + fh], [fx, fy + fh]];
      // Our point of view dollies into the monitor: the rig, its glass and
      // the picture all move as one, scaled about the same point, until the
      // monitor's screen covers the window. Nothing leaves the camera.
      const xs = glass.map((p) => p[0]), ys = glass.map((p) => p[1]);
      const gx = Math.min(...xs), gy = Math.min(...ys);
      const gw = Math.max(...xs) - gx, gh = Math.max(...ys) - gy;
      const K = Math.max(pin.width / gw, pin.height / gh);
      const k = Math.exp(Math.log(K) * z);
      const w = K === 1 ? z : (1 - 1 / k) / (1 - 1 / K);
      const cx = gx + gw / 2, cy = gy + gh / 2;
      const tx = cx * (1 - k) + (pin.width / 2 - cx) * w;
      const ty = cy * (1 - k) + (pin.height / 2 - cy) * w;
      const dolly = z > 0 ? `translate(${tx.toFixed(2)}px, ${ty.toFixed(2)}px) scale(${k.toFixed(5)})` : "";
      rig.style.transformOrigin = "0 0";
      rig.style.transform = dolly;
      if (RIG.hall_screen) {
        hallFilm.style.transformOrigin = "0 0";
        hallFilm.style.transform = dolly;
        hallIn.style.transform = `translate(${ox}px, ${oy}px) scale(${s})`;
        // 3% past the render's screen edge so none of the baked-in film
        // shows around it; the mask trims what the rig covers.
        const hq = RIG.hall_screen, hcx = hq.reduce((a, p) => a + p[0], 0) / 4, hcy = hq.reduce((a, p) => a + p[1], 0) / 4;
        hallImg.style.transform = homog(hq.map(([x, y]) => [hcx + (x - hcx) * 1.03, hcy + (y - hcy) * 1.03]));
      }
      const glassEl = cam.querySelector(".rig__glass");
      if (glassEl) { glassEl.style.transformOrigin = "0 0"; glassEl.style.transform = dolly; }
      // The glass quad isn't a perfect rectangle in perspective, so in the
      // last stretch of the move it settles onto the full frame exactly.
      const settle = clamp((z - 0.8) / 0.2);
      const q = glass.map((p, i) => {
        const m = [p[0] * k + tx, p[1] * k + ty];
        return [m[0] + (full[i][0] - m[0]) * settle, m[1] + (full[i][1] - m[1]) * settle];
      });
      scr.style.transform = homog(q);
      const o = String(1 - Math.min(1, z * 4));
      cam.querySelectorAll(".cam__call, .pan__cap").forEach((el) => (el.style.opacity = z > 0 ? o : ""));
      if (glassEl) glassEl.style.opacity = z > 0 ? String(1 - z) : "";
      const hud = String(1 - clamp((z - 0.5) / 0.4));
      cam.querySelectorAll(".cam__hud, .vf, .cam__meters, .cam__scale").forEach((el) => (el.style.opacity = z > 0 ? hud : ""));
      rig.style.opacity = "";
      // The edit bay opens on this frame with black either side, so the
      // monitor's bezel falls to black as the picture settles.
      rig.style.filter = z > 0 ? `brightness(${(1 - settle).toFixed(3)})` : "";
      // The theater behind the rig is the pin's own background; dim it too.
      rig.parentElement.style.boxShadow = z > 0 ? `inset 0 0 0 100vmax rgba(0,0,0,${settle.toFixed(3)})` : "";
    };
    camUpdate = () => {
      const top = cam.getBoundingClientRect().top + scrollY;
      const p0 = Math.max(0, Math.min(0.9999, (scrollY - top) / (cam.offsetHeight - innerHeight)));
      // The shots play over the first 86%; the rest is the hand-off, where
      // the last frame on the monitor grows until it is the whole screen.
      const p = Math.min(0.9999, p0 / 0.86);
      const zoomOut = reduced ? 0 : ease(clamp((p0 - 0.88) / 0.12));
      const zoomIn = 0;
      handoff(Math.max(zoomOut, zoomIn));
      // The monitor opens on what the roll-in left on it, the camera's live
      // view of the hall screen, then the first take comes up over it.
      const live = cam.querySelector(".cam__live");
      if (live) live.style.opacity = String(1 - clamp((p0 - 0.015) / 0.05));
      // While the monitor still shows the roll-in's picture, the hall screen
      // keeps the film the roll-in left on it, so the cut doesn't swap it.
      const rl = document.querySelector(".rollin");
      const want = p0 < 0.065 && rl ? rl.dataset.screen : (imgs[Math.min(shots.length - 1, Math.floor(clamp(Math.min(0.9999, p0 / 0.86)) * shots.length))] || {}).src;
      if (want && hallImg.getAttribute("src") !== want) hallImg.src = want;
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
        const watch = cam.querySelector(".cam__watch");
        if (watch) watch.href = sh.href;
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
      // The next shot slides in already in its "before" state (soft, too
      // bright, too warm, too tight), so it never flashes the finished look
      // and then jumps back (Parker, 2026-10-26).
      const nx = shots[i + 1], nimg = imgs[i + 1];
      if (nx && nimg) {
        const pre = {
          focus: ["blur(9px)", 1],
          nd: ["brightness(2.1) contrast(0.65)", 1],
          iris: ["brightness(1.75) contrast(0.75)", 1],
          wb: ["sepia(0.45) saturate(1.25) hue-rotate(-12deg)", 1],
          zoom: ["", 1.9],
        }[nx.kind] || ["", 1];
        nimg.style.filter = pre[0];
        nimg.style.transform = `scale(${pre[1]})`;
      }
      frame.classList.toggle("is-adjusting", e > 0 && e < 1);
      const r = cam.getBoundingClientRect();
      const inView = r.top <= 0 && r.bottom >= innerHeight;
      if (inView && k >= 1 && !rolled) { rolled = true; sfx.rec(); }
      if (!inView) rolled = false;
      // One lens-motor sound per adjustment, when it starts moving, not a
      // buzz the whole way through.
      if (inView && /focus|iris|zoom/.test(sh.kind) && e > 0 && lastE === 0 && lastServo !== i) {
        lastServo = i;
        sfx.servo();
      }
      if (e === 0) lastServo = lastServo === i ? -1 : lastServo;
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
      // The end card is Parker's own shot of himself behind the camera. As
      // you arrive, a slate is held into his frame from the right, the way
      // it comes in before a take. No masks, no circles.
      const top = iris.getBoundingClientRect().top + scrollY;
      const p = Math.max(0, Math.min(1, (scrollY - top) / (iris.offsetHeight - innerHeight)));
      // Parker walks into frame on a green screen, then the key is pulled
      // and the green becomes the real forest he shot it in. Then the slate.
      const ease = (x) => 1 - (1 - Math.max(0, Math.min(1, x))) ** 3;
      const enter = 1;
      const key = reduced ? 1 : Math.max(0, Math.min(1, (p - 0.2) / 0.05));
      const e = reduced ? 1 : ease((p - 0.34) / 0.25);
      iris.style.setProperty("--enter", enter.toFixed(3));
      iris.style.setProperty("--key", key.toFixed(3));
      iris.style.setProperty("--in", e.toFixed(3));
      // The end of the take: the shot fades to black under the first credits.
      iris.style.setProperty("--out", reduced ? "0" : Math.max(0, Math.min(1, (p - 0.86) / 0.14)).toFixed(3));
      if (key > 0.05 && !iris.dataset.keyed) { iris.dataset.keyed = "1"; sfx.chk(); }
      if (key === 0) delete iris.dataset.keyed;
      if (p > 0.55 && window.score) window.score.motif("strings");
      iris.classList.toggle("is-closed", e > 0.92);
    };
  }

  // Outro: "Where Is My Mind?" comes up as the credits start rolling and
  // carries through the star, fading the same two seconds the reel does.
  const roll = document.querySelector(".roll");
  const song = roll && roll.querySelector(".roll__song");
  if (song) {
    let lvl = 0;
    let goal = 0;
    let raf = 0;
    let t0 = 0;
    const tick = (t) => {
      const dt = t0 ? (t - t0) / 1000 : 0;
      t0 = t;
      lvl += Math.sign(goal - lvl) * Math.min(Math.abs(goal - lvl), dt / 2.2);
      try { song.volume = lvl * 0.9; } catch (err) { /* iOS volume is fixed */ }
      if (lvl <= 0.001 && goal === 0) { song.pause(); raf = 0; t0 = 0; return; }
      if (Math.abs(goal - lvl) < 0.001) { raf = 0; t0 = 0; return; }
      raf = requestAnimationFrame(tick);
    };
    let forced = false;
    const set = (on) => {
      goal = on && (sfx.on || forced) ? 1 : 0;
      if (window.score) window.score.duck(goal === 1);
      if (goal === 1 && song.paused) {
        if (song.currentTime < 14.9) song.currentTime = 14.9;
        song.play().catch(() => {});
      }
      if (!raf) raf = requestAnimationFrame(tick);
    };
    // The whole outro: the roll, the palm-tree night after it, and the star.
    const end = [roll, document.querySelector(".sky__pin"), document.querySelector(".sky"), document.querySelector(".foot")].filter(Boolean);
    const seen = new Set();
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => (en.isIntersecting ? seen.add(en.target) : seen.delete(en.target)));
      set(seen.size > 0);
    }, { threshold: 0 });
    end.forEach((el) => io.observe(el));
    // Opening End Credits from the Dock is a click, so the song can come up
    // with it even before the sound button has been touched.
    window.outroIn = () => { forced = true; set(true); };
  }

  // The last frame: after the credits, the star fades up out of black.
  const foot = document.querySelector(".foot");
  if (foot && document.body.classList.contains("is-home")) {
    const upd = () => {
      const r = foot.getBoundingClientRect();
      const p = Math.max(0, Math.min(1, (innerHeight - r.top) / (foot.offsetHeight - innerHeight * 0.2)));
      foot.style.setProperty("--fade", reduced ? 1 : Math.max(0, Math.min(1, (p - 0.25) / 0.45)).toFixed(3));
    };
    addEventListener("scroll", upd, { passive: true });
    upd();
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
    // One picture at a time. 600px between films; the next one is only
    // drawn while the camera is pushing through the current one, and it
    // never sits smaller than 78% of the frame.
    const GAP = 600;
    hall = () => {
      const top = filmsScene.getBoundingClientRect().top + scrollY;
      const p = Math.max(0, Math.min(1, (scrollY - top) / (filmsScene.offsetHeight - innerHeight)));
      const cam = p * (screens.length - 0.5) * GAP;
      screens.forEach((v, i) => {
        const z = cam - i * GAP;
        if (z > 300 || z < -GAP * 0.5) { v.style.visibility = "hidden"; return; }
        v.style.visibility = "visible";
        v.style.transform = `translateZ(${Math.max(z, -250).toFixed(1)}px)`;
        v.style.opacity = z > 0 ? Math.max(0, 1 - z / 300).toFixed(3) : "1";
        v.style.zIndex = String(screens.length - i);
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
// A screening. Clicking a film anywhere on the home page dims the room
// where you are and brings the screen up; Lights up puts you back exactly
// where you were. The film's own URL renders the same screening.
const project = (scr) => {
  const screen = scr.querySelector(".scr__screen");
  if (!screen || screen.querySelector("iframe")) return;
  if (window.score) window.score.duck(true);
  const f = document.createElement("iframe");
  f.src = screen.dataset.yt
    ? `https://www.youtube-nocookie.com/embed/${screen.dataset.yt}?autoplay=1&rel=0&modestbranding=1&playsinline=1`
    : `https://drive.google.com/file/d/${screen.dataset.drive}/preview`;
  f.title = scr.querySelector(".scr__title").textContent;
  f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
  f.allowFullscreen = true;
  screen.replaceChildren(f);
};
document.querySelectorAll(".film-page .scr").forEach((scr) => {
  scr.classList.add("is-on");
  scr.querySelector(".scr__play").addEventListener("click", () => project(scr));
});

const house = document.body.classList.contains("is-home");
let showing = null;
let lastFocus = null;
const lightsUp = (fromHistory) => {
  if (!showing) return;
  const scr = showing;
  showing = null;
  scr.classList.remove("is-on");
  document.documentElement.classList.remove("is-screening");
  if (window.score) window.score.duck(false);
  setTimeout(() => scr.remove(), 450);
  if (!fromHistory && location.pathname.startsWith("/films/")) history.back();
  if (lastFocus) lastFocus.focus({ preventScroll: true });
};
const screenFilm = (slug, push) => {
  const t = document.getElementById(`t-${slug}`);
  if (!t) return false;
  if (showing) lightsUp(true);
  const scr = t.content.firstElementChild.cloneNode(true);
  document.body.append(scr);
  showing = scr;
  lastFocus = document.activeElement;
  document.documentElement.classList.add("is-screening");
  if (push) history.pushState({ screening: slug }, "", `/films/${slug}/`);
  scr
    .querySelector(".scr__up")
    .addEventListener("click", () => lightsUp(false));
  // Click anywhere around the film to go back (Parker, 2026-10-26). The
  // screen itself, links and buttons keep their own clicks.
  scr.addEventListener("click", (ev) => {
    if (ev.target.closest(".scr__screen, a, button, iframe, video")) return;
    lightsUp(false);
  });
  scr.querySelector(".scr__play").addEventListener("click", () => project(scr));
  requestAnimationFrame(() => scr.classList.add("is-on"));
  sfx.clatter();
  // The room takes a beat to go dark, then the projector starts.
  setTimeout(() => {
    if (showing === scr) project(scr);
  }, 650);
  scr.querySelector(".scr__up").focus({ preventScroll: true });
  return true;
};
if (house) {
  document.addEventListener("click", (ev) => {
    const a = ev.target.closest && ev.target.closest('a[href^="/films/"]');
    if (!a || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.button) return;
    const slug = a.getAttribute("href").split("/")[2];
    if (screenFilm(slug, true)) ev.preventDefault();
  });
  addEventListener("keydown", (ev) => {
    if (ev.key === "Escape") lightsUp(false);
  });
  addEventListener("popstate", () => {
    const m = location.pathname.match(/^\/films\/([^/]+)/);
    if (m) screenFilm(m[1], false);
    else lightsUp(true);
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
        status.textContent = email ? "Check that email" : "Fill in every line first";
        bad[0].focus();
        return;
      }
      button.disabled = true;
      status.dataset.state = "";
      status.textContent = "Sending...";
      // FormSubmit answered in 17 to 26 s on 2026-10-26 (three tries, every
      // one slow, none failed), and with no limit the slate sat on
      // "Sending..." forever. Say so at 8 s, give up at 45 s and hand over
      // his email instead.
      const ctl = new AbortController();
      const slow = setTimeout(() => { if (status.textContent === "Sending...") status.textContent = "Still sending..."; }, 8000);
      const timer = setTimeout(() => ctl.abort(), 45000);
      try {
        const res = await fetch(form.action, {
          method: "POST",
          headers: { Accept: "application/json" },
          body: new FormData(form),
          signal: ctl.signal,
        });
        if (!res.ok) throw new Error(String(res.status));
        form.reset();
        status.dataset.state = "ok";
        status.textContent = "Sent. I'll get back to you soon.";
      } catch (err) {
        status.dataset.state = "err";
        const to = form.action.split("/").pop();
        const body = encodeURIComponent(`${form.message?.value || ""}\n\n${form.name?.value || ""}`);
        status.innerHTML = `Didn't go through. <a href="mailto:${to}?subject=${encodeURIComponent("Your next film")}&body=${body}">Email me instead</a>`;
        console.error("contact form", err);
      } finally {
        clearTimeout(timer);
        clearTimeout(slow);
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
      // The sticks come down, and the clack lands on the frame they meet.
      // Only for a real take: an incomplete slate doesn't get clapped.
      const f = slate.querySelector("form");
      if (![...f.querySelectorAll("input[required]")].every((x) => x.checkValidity())) return;
      slate.classList.remove("is-clap");
      void slate.offsetWidth;
      slate.classList.add("is-clap");
      setTimeout(() => sfx.clack(), 110);
      setTimeout(() => {
        const st = slate.querySelector(".form__status");
        if (st && st.dataset.state === "ok") slate.classList.add("is-pulled");
      }, 1400);
    });
  }
// Parker's Apple TV. Hovering an app focuses it the way the Siri Remote
// does: it lifts, tilts toward the pointer and catches the light, and the
// top shelf behind it changes. Opening one grows it out of the TV to fill
// the screen; Back, Esc or a click on the screensaver shrinks it home.
const tvEl = document.querySelector(".tv");
if (tvEl) {
  const home = tvEl.querySelector(".tvos");
  const screenBox = tvEl.querySelector(".tv__screen");
  const apps = [...tvEl.querySelectorAll(".tvos__app")];
  const focusApp = (btn) => {
    if (btn.classList.contains("is-focus")) return;
    apps.forEach((a) => a.classList.toggle("is-focus", a === btn));
    home.dataset.focus = btn.dataset.app;
    tvEl.dataset.glow = btn.dataset.app;
    sfx.tick();
  };
  apps[0].classList.add("is-focus");
  apps.forEach((btn) => {
    const icon = btn.querySelector(".tvos__icon");
    btn.addEventListener("pointerenter", () => focusApp(btn));
    btn.addEventListener("focus", () => focusApp(btn));
    btn.addEventListener("pointermove", (ev) => {
      const r = icon.getBoundingClientRect();
      const x = (ev.clientX - r.left) / r.width;
      const y = (ev.clientY - r.top) / r.height;
      icon.style.setProperty("--ry", `${((x - 0.5) * 14).toFixed(2)}deg`);
      icon.style.setProperty("--rx", `${((0.5 - y) * 12).toFixed(2)}deg`);
      icon.style.setProperty("--gx", `${(x * 100).toFixed(1)}%`);
      icon.style.setProperty("--gy", `${(y * 100).toFixed(1)}%`);
    });
    btn.addEventListener("pointerleave", () => {
      icon.style.setProperty("--rx", "0deg");
      icon.style.setProperty("--ry", "0deg");
    });
    btn.addEventListener("click", () => openApp(btn.dataset.app));
  });

  const mfx = tvEl.querySelector(".mfx");
  const aer = tvEl.querySelector(".aer");
  const billV = mfx.querySelector(".mfx__bill-v");
  let current = null;

  // FLIP: the app is laid out full screen, then drawn back down onto the
  // TV's glass and released, so it grows out of the TV.
  const fromTV = (el) => {
    const r = screenBox.getBoundingClientRect();
    return `translate(${r.left}px, ${r.top}px) scale(${r.width / innerWidth}, ${r.height / innerHeight})`;
  };
  const openApp = (name) => {
    if (current) return;
    const el = name === "mfx" ? mfx : aer;
    current = el;
    el.hidden = false;
    document.documentElement.classList.add("is-app");
    if (window.score) window.score.duck(true);
    sfx.whoosh();
    if (!reduced) {
      el.animate(
        [
          { transform: fromTV(el), borderRadius: "6px" },
          { transform: "none", borderRadius: "0" },
        ],
        { duration: 620, easing: "cubic-bezier(.2,.75,.1,1)" },
      );
    }
    if (el === mfx) {
      mfx.scrollTop = 0;
      if (!billV.src) billV.src = billV.dataset.src;
      billV.play().catch(() => {});
      mfx.querySelector(".mfx__back").focus({ preventScroll: true });
    } else startAerials();
  };
  const closeApp = () => {
    if (!current) return;
    const el = current;
    current = null;
    const done = () => {
      el.hidden = true;
      document.documentElement.classList.remove("is-app");
      if (el === mfx) billV.pause();
      else stopAerials();
      if (window.score) window.score.duck(false);
      home.querySelector(".tvos__app.is-focus").focus({ preventScroll: true });
    };
    if (reduced) return done();
    el.animate(
      [
        { transform: "none", borderRadius: "0" },
        { transform: fromTV(el), borderRadius: "6px" },
      ],
      { duration: 480, easing: "cubic-bezier(.4,0,.2,1)", fill: "forwards" },
    ).onfinish = (a) => {
      done();
      a.target.effect.target.getAnimations().forEach((x) => x.cancel());
    };
  };
  mfx.querySelector(".mfx__back").addEventListener("click", closeApp);
  addEventListener("keydown", (ev) => {
    if (ev.key !== "Escape" || !current) return;
    if (document.documentElement.classList.contains("is-screening")) return;
    closeApp();
  });

  // Aerials. Shuffled, eleven seconds a photo, two seconds of dissolve,
  // each one drifting and pushing in slightly like the real screensaver.
  let files = [];
  try {
    files = JSON.parse(aer.dataset.photos || "[]");
  } catch (err) {
    files = [];
  }
  const layers = [...aer.querySelectorAll("img")];
  let order = [];
  let idx = 0;
  let flip = 0;
  let timer = 0;
  let hintT = 0;
  const show = () => {
    if (!order.length) return;
    const img = layers[flip];
    const other = layers[1 - flip];
    const f = order[idx % order.length];
    idx += 1;
    img.onload = () => {
      img.classList.add("is-on");
      other.classList.remove("is-on");
      if (!reduced) {
        const dx = (Math.random() - 0.5) * 4;
        const dy = (Math.random() - 0.5) * 3;
        img.animate(
          [
            { transform: `scale(1.03) translate(${-dx}%, ${-dy}%)` },
            { transform: `scale(1.15) translate(${dx}%, ${dy}%)` },
          ],
          { duration: 14000, easing: "linear", fill: "forwards" },
        );
      }
    };
    img.src = `/media/photos/${f}`;
    flip = 1 - flip;
    timer = setTimeout(show, 11000);
  };
  const startAerials = () => {
    order = files.slice().sort(() => Math.random() - 0.5);
    idx = 0;
    show();
  };
  const stopAerials = () => {
    clearTimeout(timer);
    layers.forEach((l) => {
      l.classList.remove("is-on");
      l.getAnimations().forEach((a) => a.cancel());
    });
  };
  aer.addEventListener("click", closeApp);
  aer.addEventListener("pointermove", () => {
    aer.classList.add("is-moved");
    clearTimeout(hintT);
    hintT = setTimeout(() => aer.classList.remove("is-moved"), 1800);
  });
}
// The back half of the take, as one strip of film. Each section slides up
// under the last screenful of the one before it (measured, so it lines up
// at any window size) and shows itself only once it's pinned in place.
//   edit bay  ->  the window leaves full screen onto Parker's Mac
//   the Mac   ->  the Contact tab's green screen grows into the end card
const overlapUnder = (prev, next, screens = 1) => {
    if (!prev || !next) return;
    next.style.marginTop = "0px";
    if (innerWidth < 900) return;
    const end = prev.getBoundingClientRect().bottom + scrollY;
    const natural = next.getBoundingClientRect().top + scrollY;
    next.style.marginTop = `${(end - innerHeight * screens - natural).toFixed(0)}px`;
  };
const deskRun = document.querySelector(".desk-run");
const editEl = document.querySelector(".edit");
const irisEl = document.querySelector(".irisout");
const skyEl = document.querySelector(".sky");
if (
  deskRun &&
  editEl &&
  irisEl &&
  skyEl &&
  document.body.classList.contains("is-home")
) {
  // On a computer the end card lives in the Contact tab of Parker's Chrome,
  // so the Mac stays one place you click around. Opening the tab plays the
  // card: Parker on green, the key pulls to the real forest, the slate comes
  // in. On a phone it stays its own section, the way it was.
  let creditsOpen = innerWidth < 900;
  if (!creditsOpen) document.documentElement.classList.add("credits-locked");
  const cpm = document.querySelector(".cpm");
  const irisPin = irisEl.querySelector(".irisout__pin");
  const cards = [...irisPin.children];
  let inTab = false;
  const place = () => {
    const want = innerWidth >= 900 && !!cpm;
    if (want === inTab) return;
    inTab = want;
    (want ? cpm : irisPin).append(...cards);
    cpm?.classList.toggle("cpm--end", want);
    irisEl.classList.toggle("is-in-tab", want);
  };
  let played = 0;
  const play = () => {
    if (!inTab) return;
    const t0 = performance.now();
    const run = played = t0;
    const ease = (x) => 1 - (1 - Math.max(0, Math.min(1, x))) ** 3;
    const step = (now) => {
      if (played !== run) return;
      const t = reduced ? 9 : (now - t0) / 1000;
      // Green for a beat, the key pulls over 0.4s, then the slate is held in.
      cpm.style.setProperty("--enter", "1");
      cpm.style.setProperty("--key", Math.max(0, Math.min(1, (t - 0.7) / 0.4)).toFixed(3));
      cpm.style.setProperty("--in", ease((t - 1.3) / 0.9).toFixed(3));
      if (t > 0.75 && !cpm.dataset.keyed) { cpm.dataset.keyed = "1"; sfx.chk(); }
      if (t < 2.4) requestAnimationFrame(step);
    };
    delete cpm.dataset.keyed;
    requestAnimationFrame(step);
  };
  document.addEventListener("desk:page", (ev) => { if (ev.detail === "contact") play(); });
  const lay = () => {
    place();
    overlapUnder(editEl, deskRun, 2);
    // The Mac fades to black and the credits come up under it.
    if (creditsOpen || !inTab) overlapUnder(deskRun, inTab ? skyEl : irisEl);
  };
  const deskTick = () => {
    if (innerWidth < 900) return;
    const top = deskRun.getBoundingClientRect().top + scrollY;
    const span = deskRun.offsetHeight - innerHeight;
    const p = Math.max(0, Math.min(1, (scrollY - top) / span));
    // Locked, the Mac just holds at the end; open, it dissolves into the credits.
    const out = creditsOpen ? Math.max(0, Math.min(1, (p - 0.88) / 0.12)) : 0;
    deskRun.style.setProperty("--out", out.toFixed(3));
    deskRun.style.pointerEvents = out > 0.5 ? "none" : "";
  };
  // End Credits in the Dock: the way on, said the way macOS says it. One
  // bounce once the viewer has stopped on the Mac (sooner on the Contact
  // tab, where the take is over), at most twice a visit; a click rolls them.
  const reel = deskRun.querySelector(".dock__app--credits");
  if (reel) {
    // The Mac is the end of the page until End Credits is opened: no amount
    // of scrolling reaches the credits (Caleb, 2026-10-25: "the end credits
    // button should be the only way to end the credits").
    const rollCredits = () => {
      if (!creditsOpen) {
        creditsOpen = true;
        document.documentElement.classList.remove("credits-locked");
        lay();
      }
      if (window.outroIn) window.outroIn();
      // Land with the title in the middle of the window.
      requestAnimationFrame(() => {
        const t = skyEl.querySelector(".roll__pre");
        const r = t ? t.getBoundingClientRect() : null;
        const y = r ? scrollY + r.top + r.height / 2 - innerHeight / 2 : scrollY;
        scrollTo({ top: y, behavior: reduced ? "auto" : "smooth" });
      });
    };
    reel.addEventListener("click", rollCredits);
    // Premiere Pro in the Dock brings the edit bay back on screen.
    const pr = deskRun.querySelector('.dock__app[data-name="Adobe Premiere Pro"]');
    if (pr) {
      pr.style.cursor = "pointer";
      pr.addEventListener("click", () => {
        scrollTo({ top: editEl.getBoundingClientRect().top + scrollY + 2, behavior: reduced ? "auto" : "smooth" });
      });
    }
    let idleSince = performance.now(), bounces = 0, page = "flix", contactAt = 0;
    const poke = () => { idleSince = performance.now(); };
    ["scroll", "pointermove", "pointerdown", "keydown", "wheel"].forEach((t) => addEventListener(t, poke, { passive: true }));
    document.addEventListener("desk:page", (ev) => { page = ev.detail; if (page === "contact") contactAt = performance.now(); });
    setInterval(() => {
      if (bounces >= 2 || innerWidth < 900) return;
      const r = deskRun.getBoundingClientRect();
      const span = deskRun.offsetHeight - innerHeight;
      const p = -r.top / span;
      if (p < 0.05 || p > 0.86) return;
      const idle = performance.now() - idleSince;
      // 4s after the slate has settled on the Contact tab, else 9s anywhere.
      const ready = page === "contact" ? performance.now() - contactAt > 6500 && idle > 4000 : idle > 9000;
      if (!ready) return;
      bounces++;
      idleSince = performance.now();
      reel.classList.remove("is-bouncing");
      void reel.offsetWidth;
      reel.classList.add("is-bouncing");
    }, 1000);
  }
  addEventListener("scroll", deskTick, { passive: true });
  addEventListener("resize", () => { lay(); deskTick(); });
  requestAnimationFrame(() => requestAnimationFrame(() => { lay(); deskTick(); }));
  setTimeout(() => { lay(); deskTick(); }, 600);
}
// Hovering a film plays a short muted loop of it, the way his old site and
// Netflix do; a click still opens the whole film (Parker, 2026-10-26).
const hoverLoop = (host, src, place) => {
  let v = null, timer = 0;
  host.addEventListener("mouseenter", () => {
    timer = setTimeout(() => {
      const url = typeof src === "function" ? src() : src;
      if (!url) return;
      v = document.createElement("video");
      Object.assign(v, { muted: true, loop: true, playsInline: true, autoplay: true, src: url });
      v.className = "hover-loop";
      v.setAttribute("aria-hidden", "true");
      v.addEventListener("loadeddata", () => v && v.classList.add("is-on"));
      place(v);
      v.play().catch(() => {});
    }, 380);
  });
  host.addEventListener("mouseleave", () => {
    clearTimeout(timer);
    if (!v) return;
    const old = v; v = null;
    old.classList.remove("is-on");
    setTimeout(() => old.remove(), 220);
  });
};
if (matchMedia("(hover: hover) and (pointer: fine)").matches) {
  document.querySelectorAll(".mfx-tile[data-loop]").forEach((t) =>
    hoverLoop(t, t.dataset.loop, (v) => t.querySelector(".mfx-tile__img").append(v)));
  // The hall: the loop is projected into the screen's quad from the render,
  // in perspective, under the hall's own light.
  const hs = document.querySelector(".hall__stack");
  const link = hs && hs.querySelector(".hall__screen");
  if (hs && link) {
    let H = null;
    fetch("/media/hall/hall.json").then((r) => r.json()).then((j) => { H = j; }).catch(() => {});
    const homog = (q, SW, SH) => {
      const [[x0, y0], [x1, y1], [x2, y2], [x3, y3]] = q;
      const dx1 = x1 - x2, dx2 = x3 - x2, sx = x0 - x1 + x2 - x3;
      const dy1 = y1 - y2, dy2 = y3 - y2, sy = y0 - y1 + y2 - y3;
      const den = dx1 * dy2 - dx2 * dy1;
      const g = (sx * dy2 - dx2 * sy) / den, h = (dx1 * sy - sx * dy1) / den;
      const A = x1 - x0 + g * x1, B = x3 - x0 + h * x3, D = y1 - y0 + g * y1, E = y3 - y0 + h * y3;
      return `matrix3d(${A / SW},${D / SW},0,${g / SW},${B / SH},${E / SH},0,${h / SH},0,0,1,0,${x0},${y0},0,1)`;
    };
    const slug = () => (link.getAttribute("href").split("/")[2] || "");
    hoverLoop(link, () => `/media/loops/${slug()}-720.mp4`, (v) => {
      const q = H && H[slug()] && H[slug()].screen;
      if (!q) return;
      const k = hs.offsetWidth / H.size[0];
      v.classList.add("hover-loop--hall");
      v.style.transform = homog(q.map(([x, y]) => [x * k, y * k]), 960, 540);
      hs.insertBefore(v, link);
    });
  }
}

// Director: the premiere. Each film is its own render of the hall with
// that film projected and its title on the letterboard; changing film is a
// projector change, a quick dip through the dark.
const hallStack = document.querySelector(".hall__stack");
if (hallStack) {
  const fs = [...hallStack.querySelectorAll(".hall__f")];
  hallStack.closest(".scene").addEventListener("chapter", (e) => {
    fs.forEach((f, k) => f.classList.toggle("is-on", k === e.detail));
    const line = hallStack.closest(".scene").querySelectorAll(".line")[e.detail];
    const go = line && line.querySelector("a.btn");
    if (go) hallStack.querySelector(".hall__screen").href = go.getAttribute("href");
  });
}

// Then a camera rolls up the aisle into the same hall and we push into its
// monitor until the monitor is the screen. Drawn frame by frame from the
// render; the film on the hall screen and the picture on the monitor are
// mapped onto the quads the render exported for each frame.
const rollin = document.querySelector(".rollin");
if (rollin) {
  const cv = rollin.querySelector(".rollin__c");
  const cx = cv.getContext("2d");
  // 60 frames; the last is the exact view the monitor close-up was rendered
  // from, so the camera section picks up on the same object.
  const N = 60;
  const frames = [];
  let quads = null;
  const load = (src) => {
    const im = new Image();
    im.decoding = "async";
    im.src = src;
    return im;
  };
  const filmImg = load(rollin.dataset.screen);
  const monImg = load(rollin.dataset.monitor);
  const banner = `PREMIERE · ${rollin.dataset.title.toUpperCase()} · ${rollin.dataset.year}`;
  let started = false;
  const start = () => {
    if (started) return;
    started = true;
    for (let i = 1; i <= N; i++)
      frames.push(
        load(`/media/hall/rollin/${String(i).padStart(3, "0")}.webp`),
      );
    fetch("/media/hall/rollin.json")
      .then((r) => r.json())
      .then((j) => {
        quads = j;
        draw();
      })
      .catch(() => {});
  };
  new IntersectionObserver(
    ([en]) => {
      if (en.isIntersecting) start();
    },
    { rootMargin: "200% 0px" },
  ).observe(rollin);
  // Affine fit of an image onto a quad (tl, tr, bl), cover-cropped.
  // Clip to the quad (so no green shows at its edges) and cover its box.
  const fit = (img, q, s, ox, oy) => {
    if (!img.complete || !img.naturalWidth) return;
    const pts = q.map((p) => [ox + p[0] * s, oy + p[1] * s]);
    const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
    const x0 = Math.min(...xs) - 2, y0 = Math.min(...ys) - 2;
    const w = Math.max(...xs) - x0 + 2, h = Math.max(...ys) - y0 + 2;
    const ir = img.naturalWidth / img.naturalHeight;
    let dw = w, dh = w / ir;
    if (dh < h) { dh = h; dw = h * ir; }
    const c = pts.reduce((m, p) => [m[0] + p[0] / 4, m[1] + p[1] / 4], [0, 0]);
    cx.save();
    cx.beginPath();
    pts.forEach((p, k) => {
      const e2 = [p[0] + Math.sign(p[0] - c[0]) * 1.5, p[1] + Math.sign(p[1] - c[1]) * 1.5];
      if (k) cx.lineTo(e2[0], e2[1]); else cx.moveTo(e2[0], e2[1]);
    });
    cx.closePath();
    cx.clip();
    cx.drawImage(img, x0 + (w - dw) / 2, y0 + (h - dh) / 2, dw, dh);
    cx.restore();
  };
  const order = (q) => {
    // The render's last frames list the monitor's corners mirrored; sort
    // them into tl, tr, br, bl by position so the picture is never flipped.
    const pts = q.slice().sort((m, n) => m[1] - n[1]);
    const top = pts.slice(0, 2).sort((m, n) => m[0] - n[0]);
    const bot = pts.slice(2).sort((m, n) => m[0] - n[0]);
    return [top[0], top[1], bot[1], bot[0]];
  };
  const draw = () => {
    if (!started) return;
    const top = rollin.getBoundingClientRect().top + scrollY;
    const span = rollin.offsetHeight - innerHeight;
    const p = Math.max(0, Math.min(1, (scrollY - top) / span));
    const i = Math.min(N - 1, Math.floor(p * N));
    const dpr = Math.min(2, devicePixelRatio || 1);
    const W = innerWidth,
      H = innerHeight;
    if (cv.width !== Math.round(W * dpr)) {
      cv.width = Math.round(W * dpr);
      cv.height = Math.round(H * dpr);
    }
    if (cv.height !== Math.round(H * dpr)) cv.height = Math.round(H * dpr);
    cx.setTransform(1, 0, 0, 1, 0, 0);
    const f = frames[i];
    if (!f || !f.complete || !f.naturalWidth) return;
    const fw = 960,
      fh = 540;
    const s = Math.max(cv.width / fw, cv.height / fh);
    const ox = (cv.width - fw * s) / 2,
      oy = (cv.height - fh * s) / 2;
    cx.drawImage(f, ox, oy, fw * s, fh * s);
    // The film, the monitor's picture and the letterboard are in the render.
  };
  addEventListener("scroll", draw, { passive: true });
  addEventListener("resize", draw);
  setInterval(() => {
    if (
      started &&
      rollin.getBoundingClientRect().top < innerHeight &&
      rollin.getBoundingClientRect().bottom > 0
    )
      draw();
  }, 400);
}

  // The camera section slides in under the roll-in's last screenful and
  // shows itself once pinned, starting on the monitor's picture full screen.
  // The roll-in starts on the hall's last frame: overlap it, show it once pinned.
  const hallSec = document.querySelector("#films");
  if (rollin && hallSec) {
    const rpin = rollin.querySelector(".rollin__pin");
    const layR = () => overlapUnder(hallSec, rollin);
    const showR = () => { rpin.style.visibility = innerWidth >= 900 && rollin.getBoundingClientRect().top > 0.5 ? "hidden" : ""; };
    addEventListener("scroll", showR, { passive: true });
    addEventListener("resize", () => { layR(); showR(); });
    requestAnimationFrame(() => requestAnimationFrame(() => { layR(); showR(); }));
    setTimeout(() => { layR(); showR(); }, 650);
  }
  const camSec = document.querySelector(".cam");
  if (rollin && camSec) {
    const camPinEl = camSec.querySelector(".cam__pin");
    const layC = () => overlapUnder(rollin, camSec);
    const showC = () => {
      if (innerWidth < 900) { camPinEl.style.visibility = ""; return; }
      camPinEl.style.visibility = camSec.getBoundingClientRect().top > 0.5 ? "hidden" : "";
    };
    addEventListener("scroll", showC, { passive: true });
    addEventListener("resize", () => { layC(); showC(); });
    requestAnimationFrame(() => requestAnimationFrame(() => { layC(); showC(); if (camUpdate) camUpdate(); }));
    setTimeout(() => { layC(); showC(); }, 700);
  }

  // Work in progress, marked for Parker: a red frame on each part that's
  // still being built or needs his input, saying what it will become.
  const WIP = [
    [".journey__pin", "Draft render", "Low poly draft of your journey as a miniature on your table. The final renders once you like the path."],
    [".sky__pin", "Draft render", "Low poly preview of the move. Once you like it, the street renders as the real Hollywood Blvd: lit storefronts, neon and streetlights."],
  ];
  WIP.forEach(([sel, kind, text]) => {
    const el = document.querySelector(sel);
    if (!el) return;
    if (getComputedStyle(el).position === "static") el.style.position = "relative";
    const f = document.createElement("div");
    f.className = "wip";
    f.setAttribute("aria-hidden", "true");
    f.innerHTML = `<p class="wip__tag"><b>${kind}</b><span>${text}</span></p>`;
    el.appendChild(f);
  });
// Parker's table. The reel never cuts: it keeps playing on the flip
// screen of his camera, and we pull back from that screen until we're
// looking down at the whole table, then lean in to read the call sheet
// clipped to the board. One camera, one take, all of it the render's.
const knoll = document.querySelector(".knoll");
const openingEl = document.querySelector(".opening");
if (knoll && openingEl) {
  const pin = knoll.querySelector(".knoll__pin");
  const world = knoll.querySelector(".knoll__world");
  const lcd = knoll.querySelector(".knoll__lcd");
  const paper = knoll.querySelector(".knoll__paper");
  const sheet = paper.querySelector(".callsheet");
  const lctx = lcd.getContext("2d");
  const reelV = document.querySelector("#reel");
  let K = null;
  fetch("/media/rig/knoll.json")
    .then((r) => r.json())
    .then((j) => {
      K = j;
      place();
      tick();
      prints();
    })
    .catch(() => {});
  const box = (q) => {
    const xs = q.map((p) => p[0]),
      ys = q.map((p) => p[1]);
    return {
      x: Math.min(...xs),
      y: Math.min(...ys),
      w: Math.max(...xs) - Math.min(...xs),
      h: Math.max(...ys) - Math.min(...ys),
    };
  };
  const place = () => {
    if (!K) return;
    const l = box(K.lcd),
      pp = box(K.paper);
    Object.assign(lcd.style, {
      left: `${l.x}px`,
      top: `${l.y}px`,
      width: `${l.w}px`,
      height: `${l.h}px`,
    });
    Object.assign(paper.style, {
      left: `${pp.x}px`,
      top: `${pp.y}px`,
      width: `${pp.w}px`,
      height: `${pp.h}px`,
    });
    sheet.style.transform = "none";
    const sw = sheet.offsetWidth,
      sh = sheet.offsetHeight;
    // Below the clip and the polaroid tucked under it.
    // The headshot clipped to the board is part of the render; start the
    // printed sheet just under it so nothing prints over his photo
    // (Caleb, 2026-10-26, "What the tweak?" at text over the photo).
    const ph = K.objects && K.objects.polaroid_set;
    const top = ph ? Math.max(pp.h * 0.06, ph[3] - pp.y + pp.h * 0.02) : pp.h * 0.22;
    const k = Math.min((pp.w * 0.94) / sw, (pp.h - top - pp.h * 0.03) / sh);
    sheet.style.transform = `translate(${((pp.w - sw * k) / 2).toFixed(1)}px, ${top.toFixed(1)}px) scale(${k.toFixed(4)})`;
  };
  // Parker, 2026-10-26: every photo on the table opens big when clicked.
  // The render exports each print's and polaroid's box in table pixels.
  const prints = () => {
    if (!K || !K.objects || world.querySelector(".knoll__photo")) return;
    Object.entries(K.objects).forEach(([name, [x0, y0, x1, y1]]) => {
      const m = name.match(/^print_(desk-\d+)$/) || name.match(/^polaroid_(\w+)$/);
      if (!m) return;
      const src = name.startsWith("print_") ? `/media/desk/parker/${m[1]}.jpg` : `/media/desk/polaroids/${m[1]}.webp`;
      const b = document.createElement("button");
      b.type = "button";
      b.className = "knoll__photo";
      b.setAttribute("aria-label", "Open photo");
      Object.assign(b.style, { left: `${x0}px`, top: `${y0}px`, width: `${x1 - x0}px`, height: `${y1 - y0}px` });
      b.addEventListener("click", () => openPhoto(src));
      world.append(b);
    });
  };
  const openPhoto = (src) => {
    const box = document.createElement("div");
    box.className = "photo-open";
    box.innerHTML = `<img src="${src}" alt="">`;
    const shut = () => { box.classList.remove("is-on"); setTimeout(() => box.remove(), 220); removeEventListener("keydown", esc); };
    const esc = (ev) => { if (ev.key === "Escape") shut(); };
    box.addEventListener("click", shut);
    addEventListener("keydown", esc);
    document.body.append(box);
    requestAnimationFrame(() => box.classList.add("is-on"));
  };
  // A view is a world rectangle fitted to the screen.
  const view = (r, cover) => {
    const s = cover
      ? Math.max(innerWidth / r.w, innerHeight / r.h)
      : Math.min(innerWidth / r.w, innerHeight / r.h);
    return { s, cx: r.x + r.w / 2, cy: r.y + r.h / 2 };
  };
  const mix = (a, b, t) => {
    // Zoom in log space so the move reads like a dolly, not a scale.
    const s = Math.exp(Math.log(a.s) + (Math.log(b.s) - Math.log(a.s)) * t);
    const u = (1 / s - 1 / a.s) / (1 / b.s - 1 / a.s || 1);
    const w = Math.abs(b.s - a.s) < 1e-6 ? t : Math.max(0, Math.min(1, u));
    return { s, cx: a.cx + (b.cx - a.cx) * w, cy: a.cy + (b.cy - a.cy) * w };
  };
  const ease = (t) => (t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2);
  const seg = (p, a, b) => ease(Math.max(0, Math.min(1, (p - a) / (b - a))));
  const lay = () => {
    knoll.style.marginTop = "0px";
    if (innerWidth < 900) return;
    const end = openingEl.getBoundingClientRect().bottom + scrollY;
    const natural = knoll.getBoundingClientRect().top + scrollY;
    knoll.style.marginTop = `${(end - innerHeight - natural).toFixed(0)}px`;
  };
  const tick = () => {
    if (!K || innerWidth < 900) return;
    const top = knoll.getBoundingClientRect().top + scrollY;
    const span = knoll.offsetHeight - innerHeight;
    const p = Math.max(0, Math.min(1, (scrollY - top) / span));
    pin.style.visibility =
      knoll.getBoundingClientRect().top > 0.5 ? "hidden" : "";
    // The flip screen covers the window exactly the way the reel video does
    // (both 16:9, both cover), so the cut lands on the same pixels. The 0.2%
    // keeps a subpixel of bezel from showing; the old 3% zoomed the frame 6%
    // at the cut and read as a jump (2026-10-25).
    const lb = box(K.lcd);
    const L = view({ x: lb.x + lb.w * 0.002, y: lb.y + lb.h * 0.002, w: lb.w * 0.996, h: lb.h * 0.996 }, true);
    const A = view({ x: 0, y: 0, w: K.size[0], h: K.size[1] }, true);
    const pb = box(K.paper);
    const P = view(
      {
        x: pb.x - pb.w * 0.04,
        y: pb.y - pb.h * 0.04,
        w: pb.w * 1.08,
        h: pb.h * 1.08,
      },
      false,
    );
    let v;
    if (reduced) v = p < 0.4 ? A : P;
    else if (p < 0.3) v = mix(L, A, seg(p, 0.02, 0.3));
    else if (p < 0.55) v = mix(A, P, seg(p, 0.36, 0.55));
    else v = mix(P, A, seg(p, 0.86, 1));
    world.style.transform = `translate(${(innerWidth / 2 - v.cx * v.s).toFixed(2)}px, ${(innerHeight / 2 - v.cy * v.s).toFixed(2)}px) scale(${v.s.toFixed(5)})`;
  };
  // The flip screen shows the reel live, cropped the way the reel is.
  const draw = () => {
    requestAnimationFrame(draw);
    if (!reelV || reelV.readyState < 2) return;
    const r = knoll.getBoundingClientRect();
    if (r.top > innerHeight || r.bottom < 0) return;
    const vw = reelV.videoWidth,
      vh = reelV.videoHeight;
    const cr = lcd.width / lcd.height;
    let sw = vw,
      sh = vw / cr;
    if (sh > vh) {
      sh = vh;
      sw = vh * cr;
    }
    lctx.drawImage(
      reelV,
      (vw - sw) / 2,
      (vh - sh) / 2,
      sw,
      sh,
      0,
      0,
      lcd.width,
      lcd.height,
    );
  };
  requestAnimationFrame(draw);
  addEventListener("scroll", tick, { passive: true });
  addEventListener("resize", () => {
    lay();
    place();
    tick();
  });
  requestAnimationFrame(() =>
    requestAnimationFrame(() => {
      lay();
      place();
      tick();
    }),
  );
  setTimeout(() => {
    lay();
    place();
    tick();
  }, 700);
}

  // Sky over the credits, then the tilt down to the star.
  const sky = document.querySelector(".sky");
  const SKYN = sky ? Number(sky.dataset.frames) : 0;
  if (sky && SKYN > 0) {
    const cv2 = sky.querySelector(".sky__c");
    const c2 = cv2.getContext("2d");
    const fr = [];
    let started2 = false;
    const load2 = () => {
      if (started2) return;
      started2 = true;
      for (let i = 1; i <= SKYN; i++) { const im = new Image(); im.src = `/media/sky/${String(i).padStart(3, "0")}.webp`; fr.push(im); }
    };
    new IntersectionObserver(([en]) => { if (en.isIntersecting) load2(); }, { rootMargin: "200% 0px" }).observe(sky);
    // The sky holds still while the credits roll (Caleb, 2026-10-25: no
    // moving background under the text). Once the last credit has left the
    // top of the window, the whole move plays: the tilt down to the star.
    let drawnSky = -1;
    const lastCredit = () => { const r = sky.querySelector(".roll"); return r && r.lastElementChild; };
    const drawSky = () => {
      if (!started2) return;
      // The scene sits under the credits and rides up into view; once it's
      // pinned it holds a beat, then tilts down to the star.
      const end = sky.getBoundingClientRect().bottom + scrollY - innerHeight;
      const pin = sky.querySelector(".sky__pin");
      const pinned = pin ? pin.getBoundingClientRect().top <= 0.5 : true;
      // The soft top edge is only for the ride up; pinned, the frame is whole.
      if (pin) pin.classList.toggle("is-pinned", pinned);
      const hold = innerHeight * 0.35;
      const go = end - (innerWidth >= 900 ? innerHeight * 2.2 : innerHeight) + hold;
      const t = pinned ? Math.max(0, Math.min(1, (scrollY - go) / Math.max(1, end - go))) : 0;
      const i = Math.min(SKYN - 1, Math.floor(t * (SKYN - 1) + 0.0001));
      const f = fr[i];
      if (!f || !f.complete || !f.naturalWidth) return;
      const dpr = Math.min(2, devicePixelRatio || 1);
      const resized = cv2.width !== Math.round(innerWidth * dpr);
      if (resized) { cv2.width = Math.round(innerWidth * dpr); cv2.height = Math.round(innerHeight * dpr); }
      // Redraw only when the frame changes. The sky holds one frame through
      // the whole roll, and repainting a full-window canvas on every scroll
      // event under the credits is what made the roll stutter (2026-10-25).
      if (!resized && i === drawnSky) return;
      drawnSky = i;
      const s2 = Math.max(cv2.width / f.naturalWidth, cv2.height / f.naturalHeight);
      c2.drawImage(f, (cv2.width - f.naturalWidth * s2) / 2, (cv2.height - f.naturalHeight * s2) / 2, f.naturalWidth * s2, f.naturalHeight * s2);
    };
    addEventListener("scroll", drawSky, { passive: true });
    addEventListener("resize", drawSky);
    setInterval(drawSky, 500);
    // The footer is the star the tilt lands on, so it doesn't fade in.
    const ft = document.querySelector(".foot");
    if (ft) ft.classList.add("is-landed");
  }
})();

// Where you are, faintly, beside the sound button, and a way to jump if you
// don't want to scroll the whole take (Parker, 2026-10-26: "non-intrusive
// visually", "just in case somebody doesn't want to scroll through").
(() => {
  if (!document.body.classList.contains("is-home")) return;
  const sound = document.querySelector(".mast__sound");
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!sound) return;
  // Parker's own menu, 2026-10-26: Home, About Me, Featured Films, All Films,
  // Photography, Contact me. The last three are tabs on his Mac.
  const PARTS = [
    [".opening", "Home"], [".knoll", "About Me"], [".scene--films", "Featured Films"],
    [".desk-run", "All Films", "flix"], [".desk-run", "Photography", "gram"], [".desk-run", "Contact me", "contact"],
  ].map(([sel, name, tab]) => [document.querySelector(sel), name, tab]).filter(([el]) => el);
  const wrap = document.createElement("div");
  wrap.className = "where";
  wrap.innerHTML = '<button class="where__now" type="button" aria-expanded="false" aria-haspopup="true"></button><ol class="where__list" hidden></ol>';
  const now = wrap.querySelector(".where__now");
  const list = wrap.querySelector(".where__list");
  PARTS.forEach(([el, name, tab]) => {
    const li = document.createElement("li");
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = name;
    b.addEventListener("click", () => {
      close();
      // Tabs on the Mac: land in the middle of the Mac and bring that tab up.
      const y = tab ? el.getBoundingClientRect().top + scrollY + (el.offsetHeight - innerHeight) * 0.5 : el.getBoundingClientRect().top + scrollY + 2;
      scrollTo({ top: y, behavior: reduced ? "auto" : "smooth" });
      if (tab && window.desk) setTimeout(() => window.desk.open(tab), reduced ? 0 : 700);
    });
    li.append(b);
    list.append(li);
  });
  document.body.append(wrap);
  const close = () => { list.hidden = true; now.setAttribute("aria-expanded", "false"); };
  now.addEventListener("click", () => {
    const open = list.hidden;
    list.hidden = !open;
    now.setAttribute("aria-expanded", String(open));
  });
  document.addEventListener("click", (ev) => { if (!wrap.contains(ev.target)) close(); });
  addEventListener("keydown", (ev) => { if (ev.key === "Escape") close(); });
  const place = () => {
    const r = sound.getBoundingClientRect();
    wrap.style.right = `${Math.round(innerWidth - r.left + 12)}px`;
    wrap.style.top = `${Math.round(r.top + r.height / 2)}px`;
    let cur = PARTS[0][1];
    const page = window.desk && window.desk.page ? window.desk.page() : "flix";
    for (const [el, name, tab] of PARTS) {
      const r = el.getBoundingClientRect();
      if (!r.height) continue;
      if (tab && tab !== page) continue; // on the Mac, the open tab names where you are
      if (r.top <= innerHeight * 0.5) cur = name;
    }
    if (now.textContent !== cur) now.textContent = cur;
    wrap.classList.toggle("is-hidden", document.documentElement.classList.contains("has-leader") || document.documentElement.classList.contains("is-screening"));
  };
  addEventListener("scroll", place, { passive: true });
  addEventListener("resize", place);
  setInterval(place, 1000);
  place();
})();

// My Journey: Parker's drive and flight as a miniature on his own table,
// scrubbed by scroll, with his five lines above it (his notes, 2026-10-26).
// Beat frame ranges come from the render's beats_hint.
(() => {
  const jy = document.querySelector(".journey");
  if (!jy || innerWidth < 900) return;
  const N = Number(jy.dataset.frames) || 48;
  const cv = jy.querySelector(".journey__c"), cx = cv.getContext("2d");
  const pin = jy.querySelector(".journey__pin");
  const beats = [...jy.querySelectorAll(".jy__beat")];
  // frame where each line takes over: start, Colorado, mid-Colorado, airport and LA, USC
  const AT = [1, 7, 13, 19, 33];
  const fr = [];
  let on = false;
  const load = () => {
    if (on) return; on = true;
    for (let i = 1; i <= N; i++) { const im = new Image(); im.src = `/media/journey/frames/${String(i).padStart(3, "0")}.webp`; fr.push(im); }
  };
  new IntersectionObserver(([en]) => { if (en.isIntersecting) load(); }, { rootMargin: "150% 0px" }).observe(jy);
  // Cut from the whole table straight into the miniature: the journey slides
  // under the table's last screenful and shows itself once pinned.
  const kn = document.querySelector(".knoll");
  const lay = () => {
    jy.style.marginTop = "0px";
    if (!kn) return;
    const end = kn.getBoundingClientRect().bottom + scrollY;
    const natural = jy.getBoundingClientRect().top + scrollY;
    jy.style.marginTop = `${(end - innerHeight - natural).toFixed(0)}px`;
  };
  requestAnimationFrame(() => requestAnimationFrame(lay));
  setTimeout(lay, 800);
  addEventListener("resize", lay);
  let drawn = -1;
  const draw = () => {
    if (!on) return;
    const r = jy.getBoundingClientRect();
    pin.style.visibility = r.top > 0.5 ? "hidden" : "";
    const p = Math.max(0, Math.min(1, -r.top / Math.max(1, jy.offsetHeight - innerHeight)));
    const i = Math.min(N - 1, Math.floor(p * N));
    const f = fr[i];
    const beat = AT.reduce((b, at, k) => (i + 1 >= at ? k : b), 0);
    beats.forEach((b, k) => b.classList.toggle("is-on", k === beat && i < N - 3));
    if (!f || !f.complete || !f.naturalWidth) return;
    const dpr = Math.min(2, devicePixelRatio || 1);
    const W = Math.round(innerWidth * dpr), H = Math.round(innerHeight * dpr);
    const resized = cv.width !== W || cv.height !== H;
    if (resized) { cv.width = W; cv.height = H; }
    if (!resized && i === drawn) return;
    drawn = i;
    const s = Math.max(W / f.naturalWidth, H / f.naturalHeight);
    cx.drawImage(f, (W - f.naturalWidth * s) / 2, (H - f.naturalHeight * s) / 2, f.naturalWidth * s, f.naturalHeight * s);
  };
  addEventListener("scroll", draw, { passive: true });
  addEventListener("resize", draw);
  setInterval(draw, 400);
})();
