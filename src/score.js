/* The sound score. Every cue is synthesised with Web Audio unless a real
   recording is listed in this script tag's data-samples (files in
   media/sfx/, "clack.webm clack.mp3 motif-piano.mp3"), which then wins.
   Nothing plays until score.unlock() runs inside the visitor's first click
   or key, and nothing plays while score.on is false. */
(() => {
  const AC = window.AudioContext || window.webkitAudioContext;
  const OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
  const me = document.currentScript;
  const BASE = (me && me.dataset.base) || "/media/sfx/";
  const LIST = ((me && me.dataset.samples) || "")
    .split(/[\s,]+/)
    .filter(Boolean);
  const db = (d) => Math.pow(10, d / 20);
  const hz = (s) => 146.832 * Math.pow(2, s / 12); // semitones above D3
  const rnd = (a, b) => a + Math.random() * (b - a);
  let on = true;
  try {
    on = sessionStorage.getItem("sound") !== "off";
  } catch (e) {
    on = true;
  }
  let E = null;
  let ducked = false;
  const samples = {};
  const last = {};
  const played = {};

  // One graph per context: cues into sfx, motifs into mus (the bus that
  // ducks), both through a safety limiter at -1 dBFS. At -6 Chrome added
  // automatic makeup gain and the -20 dBFS 2-pop measured -17.5.
  const engine = (c, live) => {
    const lim = c.createDynamicsCompressor();
    lim.threshold.value = -1;
    lim.knee.value = 0;
    lim.ratio.value = 20;
    lim.attack.value = 0.002;
    lim.release.value = 0.15;
    const master = c.createGain();
    master.gain.value = live && !on ? 0 : 1;
    master.connect(lim).connect(c.destination);
    const sfx = c.createGain();
    sfx.connect(master);
    const mus = c.createGain();
    mus.connect(master);
    const sr = c.sampleRate;
    const noise = c.createBuffer(1, sr, sr);
    const nd = noise.getChannelData(0);
    for (let i = 0; i < sr; i++) nd[i] = Math.random() * 2 - 1;
    // A small hall for the motifs: 2.2 s of decaying noise.
    const rev = c.createConvolver();
    const n = (sr * 2.2) | 0,
      ir = c.createBuffer(2, n, sr);
    for (let ch = 0; ch < 2; ch++) {
      const d = ir.getChannelData(ch);
      for (let i = 0; i < n; i++)
        d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / n, 4);
    }
    rev.buffer = ir;
    const wet = c.createGain();
    wet.gain.value = 0.3;
    rev.connect(wet).connect(mus);
    const vox = c.createGain();
    vox.connect(mus);
    vox.connect(rev);
    return { c, master, sfx, mus, vox, noise, ks: {} };
  };

  const env = (p, t, a, pk, d) => {
    p.setValueAtTime(0.0001, t);
    p.exponentialRampToValueAtTime(pk, t + a);
    p.exponentialRampToValueAtTime(0.0001, t + a + d);
  };
  // Filtered noise burst.
  const nz = (E, t, d, f, q, pk, type = "bandpass", a = 0.001, out = E.sfx) => {
    const c = E.c,
      s = c.createBufferSource(),
      b = c.createBiquadFilter(),
      g = c.createGain();
    s.buffer = E.noise;
    s.loop = true;
    b.type = type;
    b.frequency.value = f;
    b.Q.value = q;
    env(g.gain, t, a, pk, d);
    s.connect(b).connect(g).connect(out);
    s.start(t, Math.random() * 0.9);
    s.stop(t + a + d + 0.05);
    return b;
  };
  // Oscillator with an optional pitch glide to f2.
  const os = (E, t, type, f, d, pk, a = 0.002, out = E.sfx, f2) => {
    const c = E.c,
      o = c.createOscillator(),
      g = c.createGain();
    o.type = type;
    o.frequency.setValueAtTime(f, t);
    if (f2) o.frequency.exponentialRampToValueAtTime(f2, t + a + d);
    env(g.gain, t, a, pk, d);
    o.connect(g).connect(out);
    o.start(t);
    o.stop(t + a + d + 0.05);
    return o;
  };
  // Sparse random impulses: paper fibres tearing, CRT static.
  const crackle = (E, t, d, dens, shape, hp, pk) => {
    const c = E.c,
      sr = c.sampleRate,
      n = (sr * d) | 0,
      b = c.createBuffer(1, n, sr),
      x = b.getChannelData(0);
    for (let i = 0; i < n; i++)
      if (Math.random() < dens) x[i] = (Math.random() * 2 - 1) * shape(i / n);
    const s = c.createBufferSource(),
      f = c.createBiquadFilter(),
      g = c.createGain();
    s.buffer = b;
    f.type = "highpass";
    f.frequency.value = hp;
    g.gain.value = pk;
    s.connect(f).connect(g).connect(E.sfx);
    s.start(t);
  };
  // A gain node with a flat top: attack a, hold to t+d-r, release r.
  const bus = (E, t, d, a, r, pk = 1, out = E.sfx) => {
    const g = E.c.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(pk, t + a);
    g.gain.setValueAtTime(pk, t + d - r);
    g.gain.exponentialRampToValueAtTime(0.0001, t + d);
    g.connect(out);
    return g;
  };

  // The SMPTE 2-pop: 1 kHz at -20 dBFS for exactly one frame at 24 fps.
  const pop = (E, t) => {
    const o = E.c.createOscillator(),
      g = E.c.createGain(),
      L = 1 / 24,
      v = db(-20);
    o.frequency.value = 1000;
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(v, t + 0.0005);
    g.gain.setValueAtTime(v, t + L - 0.0005);
    g.gain.linearRampToValueAtTime(0, t + L);
    o.connect(g).connect(E.sfx);
    o.start(t);
    o.stop(t + L + 0.01);
  };

  const C = {
    pop2: { len: 0.1, f: pop },
    tailpop: { len: 0.1, f: pop },
    // Projector: motor hum and fan under the claw, which spins up to 24 a second.
    clatter: {
      len: 2.8,
      trim: -3,
      f(E, t, o) {
        const d = o.dur || 2.6,
          c = E.c,
          bed = bus(E, t, d, 0.35, 0.35, 1);
        const m = c.createOscillator(),
          ml = c.createBiquadFilter(),
          mg = c.createGain();
        m.type = "sawtooth";
        m.frequency.setValueAtTime(48, t);
        m.frequency.linearRampToValueAtTime(96, t + 0.4);
        ml.type = "lowpass";
        ml.frequency.value = 320;
        mg.gain.value = 0.05;
        m.connect(ml).connect(mg).connect(bed);
        m.start(t);
        m.stop(t + d + 0.05);
        nz(E, t, d, 700, 0.5, 0.035, "lowpass", 0.3, bed);
        for (let x = t; x < t + d - 0.02; ) {
          const j = rnd(0.8, 1.1);
          nz(E, x, 0.006, 2900, 1.8, 0.5 * j, "bandpass", 0.0008, bed);
          nz(E, x + 0.004, 0.014, 420, 1.2, 0.35 * j, "bandpass", 0.001, bed);
          x +=
            1 / (24 * Math.min(1, 0.55 + ((x - t) / 0.4) * 0.45)) +
            rnd(-0.0008, 0.0008);
        }
      },
    },
    // Ticket stub torn along its perforation, then the snap as it comes free.
    rip: {
      len: 0.45,
      trim: -10,
      f(E, t) {
        crackle(E, t, 0.3, 0.09, (p) => Math.sqrt(p) * rnd(0.5, 1), 1100, 0.5);
        nz(E, t, 0.28, 3200, 0.8, 0.03, "bandpass", 0.12);
        nz(E, t + 0.3, 0.02, 2500, 0.9, 0.5);
      },
    },
    // A tape splice crossing the gate: a soft low thup and the tape's tick.
    splice: {
      len: 0.2,
      trim: 2,
      f(E, t) {
        os(E, t, "sine", 90, 0.07, 0.07, 0.002, E.sfx, 40);
        nz(E, t, 0.008, 1500, 1, 0.12);
      },
    },
    // Split-flap marquee: a flap releases and lands, letter by letter.
    flap: {
      len: 0.8,
      trim: -2,
      gap: 120,
      f(E, t, o) {
        const n = Math.min(o.n || 8, 24);
        for (let i = 0; i < n; i++) {
          const x = t + i * 0.028 + rnd(0, 0.004),
            v = rnd(0.8, 1) * (1 - i / 60);
          nz(E, x, 0.005, 3600, 2, 0.32 * v);
          nz(E, x + 0.011, 0.008, 1700, 1.5, 0.22 * v);
        }
      },
    },
    // A laurel stamped on the poster: rubber on paper on a desk.
    stamp: {
      len: 0.25,
      f(E, t) {
        os(E, t, "sine", 120, 0.12, 0.25, 0.002, E.sfx, 50);
        nz(E, t, 0.05, 350, 0.7, 0.35, "lowpass");
        nz(E, t + 0.002, 0.025, 1400, 0.8, 0.3);
      },
    },
    // Camera rolling: one short soft beep.
    rec: {
      len: 0.15,
      trim: 2,
      f(E, t) {
        os(E, t, "sine", 1760, 0.075, db(-27), 0.003);
        os(E, t, "sine", 3520, 0.05, db(-42), 0.003);
      },
    },
    // Lens motor: a small geared whine while focus, iris or zoom moves.
    servo: {
      len: 0.35,
      trim: 8,
      gap: 70,
      f(E, t, o) {
        const d = o.dur || 0.22,
          c = E.c,
          g = bus(E, t, d, 0.02, 0.04, 1);
        const w = c.createOscillator(),
          b = c.createBiquadFilter(),
          wg = c.createGain();
        w.type = "sawtooth";
        w.frequency.setValueAtTime(600, t);
        w.frequency.linearRampToValueAtTime(680, t + d);
        b.type = "bandpass";
        b.frequency.value = 1300;
        b.Q.value = 2;
        wg.gain.value = 0.012;
        w.connect(b).connect(wg).connect(g);
        w.start(t);
        w.stop(t + d + 0.05);
        nz(E, t, d, 5200, 3, 0.03, "bandpass", 0.01, g);
      },
    },
    // The playhead crossing a cut.
    tick: {
      len: 0.06,
      gap: 30,
      f(E, t) {
        nz(E, t, 0.004, 5000, 0.7, 0.06, "highpass");
        os(E, t, "sine", 1250, 0.018, 0.035, 0.001);
      },
    },
    // A push or iris transition: air swept up and across.
    whoosh: {
      len: 0.7,
      trim: 2,
      gap: 250,
      f(E, t, o) {
        const d = o.dur || 0.55,
          c = E.c,
          s = c.createBufferSource(),
          b = c.createBiquadFilter(),
          g = c.createGain();
        s.buffer = E.noise;
        s.loop = true;
        b.type = "bandpass";
        b.Q.value = 1.1;
        b.frequency.setValueAtTime(250, t);
        b.frequency.exponentialRampToValueAtTime(2600, t + d * 0.55);
        b.frequency.exponentialRampToValueAtTime(700, t + d);
        g.gain.setValueAtTime(0.0001, t);
        g.gain.exponentialRampToValueAtTime(0.22, t + d * 0.5);
        g.gain.exponentialRampToValueAtTime(0.0001, t + d);
        let out = E.sfx;
        if (c.createStereoPanner) {
          const p = c.createStereoPanner();
          p.pan.setValueAtTime(-0.6, t);
          p.pan.linearRampToValueAtTime(0.6, t + d);
          p.connect(E.sfx);
          out = p;
        }
        s.connect(b).connect(g).connect(out);
        s.start(t);
        s.stop(t + d + 0.05);
      },
    },
    // SLR: mirror up and first curtain, then 30 ms later the second curtain.
    shutter: {
      len: 0.2,
      trim: -2,
      f(E, t) {
        nz(E, t, 0.01, 2600, 1.2, 0.5);
        os(E, t, "sine", 160, 0.03, 0.12, 0.001, E.sfx, 90);
        nz(E, t + 0.03, 0.008, 3800, 1.4, 0.45);
        nz(E, t + 0.031, 0.03, 900, 1, 0.25);
        os(E, t + 0.03, "sine", 210, 0.04, 0.12, 0.001, E.sfx, 110);
        nz(E, t + 0.07, 0.02, 5000, 2, 0.06);
      },
    },
    // Flash recharging: the rising capacitor whine, then the ready blip.
    flash: {
      len: 1.8,
      trim: 2,
      f(E, t) {
        const c = E.c,
          o = c.createOscillator(),
          g = bus(E, t, 1.5, 0.06, 0.12, db(-34));
        o.type = "triangle";
        o.frequency.setValueAtTime(1500, t);
        o.frequency.exponentialRampToValueAtTime(7600, t + 1.5);
        o.connect(g);
        o.start(t);
        o.stop(t + 1.55);
        os(E, t + 1.58, "sine", 3200, 0.03, db(-36), 0.002);
      },
    },
    // Carousel slide change: the solenoid, the tray, the slide dropping in.
    chk: {
      len: 0.25,
      gap: 90,
      f(E, t) {
        nz(E, t, 0.012, 2200, 1.3, 0.4);
        nz(E, t + 0.006, 0.03, 700, 1, 0.25);
        nz(E, t + 0.03, 0.05, 1600, 2, 0.05);
        nz(E, t + 0.11, 0.015, 1900, 1.2, 0.35);
        os(E, t + 0.11, "sine", 260, 0.05, 0.12, 0.001, E.sfx, 140);
      },
    },
    // Clapper sticks: one hard wooden crack and the room answering it.
    clack: {
      len: 0.2,
      trim: -4,
      gap: 300,
      f(E, t) {
        nz(E, t, 0.028, 1900, 0.7, 1);
        nz(E, t, 0.006, 5000, 0.9, 0.5, "highpass");
        os(E, t, "triangle", 820, 0.045, 0.12, 0.0008, E.sfx, 760);
        nz(E, t + 0.011, 0.03, 1500, 0.7, 0.25);
        nz(E, t + 0.023, 0.04, 1100, 0.7, 0.14);
      },
    },
    // CRT powering on: the thump, a crackle of static, the flyback whine.
    crt: {
      len: 1.1,
      trim: -2,
      f(E, t) {
        os(E, t, "sine", 70, 0.18, 0.25, 0.003, E.sfx, 32);
        nz(E, t, 0.08, 220, 0.8, 0.3, "lowpass");
        crackle(
          E,
          t + 0.01,
          0.45,
          0.004,
          (p) => Math.pow(1 - p, 2),
          2000,
          0.25,
        );
        os(E, t + 0.02, "sine", 15734, 0.9, db(-46), 0.15);
      },
    },
    // Tape stop: a buffer slowed to a halt with playbackRate. Pass
    // opts.buffer to stop real audio, else a held D major chord.
    tapestop: {
      len: 1.2,
      trim: 5,
      f(E, t, o) {
        const c = E.c,
          s = c.createBufferSource(),
          lp = c.createBiquadFilter(),
          g = c.createGain();
        s.buffer = o.buffer || chord(E);
        s.playbackRate.setValueAtTime(1, t + 0.2);
        s.playbackRate.exponentialRampToValueAtTime(0.06, t + 0.95);
        lp.type = "lowpass";
        lp.frequency.value = 2500;
        g.gain.setValueAtTime(0.0001, t);
        g.gain.exponentialRampToValueAtTime(o.buffer ? 0.5 : 0.09, t + 0.02);
        g.gain.setValueAtTime(o.buffer ? 0.5 : 0.09, t + 0.7);
        g.gain.exponentialRampToValueAtTime(0.0001, t + 1);
        s.connect(lp).connect(g).connect(E.sfx);
        s.start(t);
        s.stop(t + 1.05);
      },
    },
    // Rewind: the tape squeal climbing, then the transport clunks to a stop.
    rewind: {
      len: 1.1,
      trim: -4,
      f(E, t) {
        const c = E.c,
          o = c.createOscillator(),
          b = c.createBiquadFilter(),
          g = bus(E, t, 0.85, 0.05, 0.05, 0.05);
        const l = c.createOscillator(),
          lg = c.createGain(),
          tr = c.createGain();
        o.type = "sawtooth";
        o.frequency.setValueAtTime(300, t);
        o.frequency.exponentialRampToValueAtTime(2200, t + 0.85);
        b.type = "bandpass";
        b.frequency.value = 1500;
        b.Q.value = 0.9;
        l.type = "square";
        l.frequency.value = 28;
        lg.gain.value = 0.4;
        tr.gain.value = 0.6;
        l.connect(lg).connect(tr.gain);
        o.connect(b).connect(tr).connect(g);
        o.start(t);
        l.start(t);
        o.stop(t + 0.9);
        l.stop(t + 0.9);
        nz(E, t + 0.86, 0.02, 600, 1, 0.3);
        os(E, t + 0.86, "sine", 150, 0.05, 0.15, 0.001, E.sfx, 80);
      },
    },
    // The film tail slapping the take-up reel as it spins down.
    runout: {
      len: 2.8,
      f(E, t) {
        let x = t,
          dt = 0.05,
          a = 1;
        for (let i = 0; i < 14; i++) {
          nz(E, x, 0.018, 1100, 0.9, 0.35 * a);
          os(E, x, "sine", 170, 0.03, 0.1 * a, 0.001, E.sfx, 110);
          x += dt;
          dt *= 1.18;
          a *= 0.86;
        }
      },
    },
  };
  C.beep = C.pop2;

  // Held D major for the synthetic tape stop, made once per context.
  const chord = (E) => {
    if (E.chord) return E.chord;
    const sr = E.c.sampleRate,
      n = (sr * 1.1) | 0,
      b = E.c.createBuffer(1, n, sr),
      x = b.getChannelData(0);
    [0, 7, 16].forEach((s) => {
      const f = hz(s);
      for (let h = 1; h <= 6; h++) {
        const w = (2 * Math.PI * f * h) / sr,
          a = 0.12 / h;
        for (let i = 0; i < n; i++) x[i] += a * Math.sin(w * i);
      }
    });
    return (E.chord = b);
  };

  // Instruments. Each plays one note: (E, t, freq, dur, level).
  const brass = (E, t, f, d, v) => {
    const c = E.c,
      lp = c.createBiquadFilter(),
      g = c.createGain(),
      r = 0.18;
    lp.type = "lowpass";
    lp.Q.value = 0.8;
    lp.frequency.setValueAtTime(f * 1.2, t);
    lp.frequency.exponentialRampToValueAtTime(Math.min(f * 7, 5000), t + 0.07);
    lp.frequency.exponentialRampToValueAtTime(Math.min(f * 4, 3500), t + 0.25);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(v, t + 0.05);
    g.gain.setValueAtTime(v, t + d);
    g.gain.exponentialRampToValueAtTime(0.0001, t + d + r);
    const l = c.createOscillator(),
      lg = c.createGain();
    l.frequency.value = 5;
    lg.gain.setValueAtTime(0, t);
    lg.gain.linearRampToValueAtTime(d > 0.8 ? 7 : 0, t + 0.7);
    l.connect(lg);
    l.start(t);
    l.stop(t + d + r);
    [-7, 7].forEach((cents) => {
      const o = c.createOscillator();
      o.type = "sawtooth";
      o.frequency.value = f;
      o.detune.value = cents;
      lg.connect(o.detune);
      o.connect(lp);
      o.start(t);
      o.stop(t + d + r);
    });
    lp.connect(g).connect(E.vox);
  };
  // Struck bars: a bright fundamental, a fourth partial that dies fast, a tink.
  const celesta = (E, t, f, d, v) => {
    [
      [1, 1, 1.4],
      [2, 0.06, 0.5],
      [4, 0.22, 0.22],
      [9.3, 0.05, 0.05],
    ].forEach(([m, a, T]) => {
      const fm = f * m;
      if (fm < 16000) os(E, t, "sine", fm, T * 3, v * a, 0.0015, E.vox);
    });
  };
  // Stiff strings: slightly sharp partials, the high ones decaying first,
  // two strings per note beating against each other, and the hammer.
  const piano = (E, t, f, d, v) => {
    const c = E.c,
      T = Math.min(d + 1.2, 3.2);
    for (let n = 1; n <= 8; n++) {
      const fn = f * n * Math.sqrt(1 + 0.0004 * n * n);
      if (fn > 12000) break;
      const a = v * Math.pow(n, -1.15) * (n === 1 ? 1 : 0.8),
        tc = (T / (6.9 * (0.6 + 0.35 * n))) * 3;
      [-1.2, 1.2].forEach((cents) => {
        const o = c.createOscillator(),
          g = c.createGain();
        o.frequency.value = fn;
        o.detune.value = cents * n * 0.5;
        g.gain.setValueAtTime(0, t);
        g.gain.linearRampToValueAtTime(a / 2, t + 0.003);
        g.gain.setTargetAtTime(0, t + 0.003, tc);
        o.connect(g).connect(E.vox);
        o.start(t);
        o.stop(t + T + 0.1);
      });
    }
    nz(E, t, 0.02, 1800, 0.6, v * 0.25, "lowpass", 0.001, E.vox);
  };
  // Karplus-Strong: a burst of noise ringing in a delay line one period long.
  const ks = (E, f) => {
    const key = f.toFixed(2);
    if (E.ks[key]) return E.ks[key];
    const sr = E.c.sampleRate,
      n = (sr * 2.6) | 0,
      N = Math.max(2, Math.round(sr / f - 0.5));
    const b = E.c.createBuffer(1, n, sr),
      y = b.getChannelData(0);
    for (let i = 0; i < N; i++)
      y[i] = (Math.random() * 2 - 1 + (i ? y[i - 1] : 0)) * 0.5;
    for (let i = N; i < n; i++)
      y[i] = 0.996 * 0.5 * (y[i - N] + y[i - N - 1 < 0 ? 0 : i - N - 1]);
    return (E.ks[key] = b);
  };
  const guitar = (E, t, f, d, v) => {
    const c = E.c,
      s = c.createBufferSource(),
      lp = c.createBiquadFilter(),
      body = c.createBiquadFilter(),
      g = c.createGain();
    s.buffer = ks(E, f);
    lp.type = "lowpass";
    lp.frequency.value = 3200;
    body.type = "peaking";
    body.frequency.value = 200;
    body.Q.value = 1.2;
    body.gain.value = 4;
    g.gain.value = v;
    s.connect(lp).connect(body).connect(g).connect(E.vox);
    s.start(t);
  };
  // Section strings: three detuned saws per voice, slow bow, gentle vibrato.
  const strings = (E, t, f, d, v) => {
    const c = E.c,
      lp = c.createBiquadFilter(),
      g = c.createGain(),
      r = 1.2;
    lp.type = "lowpass";
    lp.frequency.value = 1500;
    lp.Q.value = 0.3;
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(v, t + 0.45);
    g.gain.setValueAtTime(v, t + d);
    g.gain.linearRampToValueAtTime(0, t + d + r);
    const l = c.createOscillator(),
      lg = c.createGain();
    l.frequency.value = 5.2;
    lg.gain.value = 4;
    l.connect(lg);
    l.start(t);
    l.stop(t + d + r);
    [-9, 0, 9].forEach((cents) => {
      const o = c.createOscillator();
      o.type = "sawtooth";
      o.frequency.value = f;
      o.detune.value = cents;
      lg.connect(o.detune);
      o.connect(lp);
      o.start(t);
      o.stop(t + d + r);
    });
    lp.connect(g).connect(E.vox);
  };

  // The theme: D, up a fifth to A, then G and down to a held F sharp.
  // [semitones above D3, seconds].
  const THEME = [
    [12, 0.32],
    [19, 0.64],
    [17, 0.32],
    [16, 1.9],
  ];
  // v is set so each motif peaks near -14 dBFS (strings -16) offline.
  // k stretches time, oct shifts the theme, dbl doubles it, chord sits
  // under the last note, strum spreads that chord like a pick.
  const M = {
    brass: {
      fn: brass,
      k: 1,
      oct: 0,
      dbl: -12,
      chord: [0, 7],
      v: 0.0460,
      len: 4,
    },
    celesta: { fn: celesta, k: 0.9, oct: 12, chord: [24], v: 0.0750, len: 5 },
    piano: { fn: piano, k: 1.1, oct: 0, chord: [-12, 0, 7], v: 0.0441, len: 6 },
    guitar: {
      fn: guitar,
      k: 1,
      oct: 0,
      chord: [0, 7, 12],
      strum: 0.018,
      v: 0.1630,
      len: 5,
    },
    strings: {
      fn: strings,
      k: 1.6,
      oct: 0,
      chord: [-12, 0, 7, 12],
      v: 0.0258,
      len: 7,
    },
  };
  const motif = (E, t, name) => {
    const m = M[name];
    let x = t;
    THEME.forEach(([s, d], i) => {
      const dur = d * m.k,
        f = hz(s + m.oct),
        lastNote = i === THEME.length - 1;
      if (lastNote && m.chord)
        m.chord.forEach((cs, j) => {
          const at = m.strum ? x - (m.chord.length - j) * m.strum : x;
          m.fn(E, at, hz(cs), dur, m.v * 0.6);
        });
      m.fn(E, x, f, dur, m.v);
      if (m.dbl) m.fn(E, x, hz(s + m.oct + m.dbl), dur, m.v * 0.5);
      x += dur;
    });
  };

  // A cue's own bus: its trim in dB (set from the offline peak test) times
  // opts.gain.
  const route = (E, cue, gain) => {
    const k = db(cue.trim || 0) * (gain || 1);
    if (k === 1) return E;
    const g = E.c.createGain();
    g.gain.value = k;
    g.connect(E.sfx);
    return Object.assign({}, E, { sfx: g });
  };
  const playSample = (E, t, s, out) => {
    const src = E.c.createBufferSource(),
      g = E.c.createGain();
    src.buffer = s.buf;
    g.gain.value = s.gain;
    src.connect(g).connect(out);
    src.start(t);
  };
  // Load listed recordings, one per cue, normalised to that cue's peak.
  const PEAK = { motif: -14, clack: -10, pop2: -20, tailpop: -20, beep: -20 };
  const load = () => {
    const probe = document.createElement("audio");
    const ok = (f) =>
      probe.canPlayType(
        /\.webm$/.test(f)
          ? 'audio/webm; codecs="opus"'
          : /\.mp3$/.test(f)
            ? "audio/mpeg"
            : "audio/wav",
      ) !== "";
    LIST.forEach((file) => {
      const name = file.replace(/\.[^.]+$/, "");
      if (samples[name] !== undefined || !ok(file)) return;
      samples[name] = null;
      fetch(BASE + file)
        .then((r) => (r.ok ? r.arrayBuffer() : Promise.reject(r.status)))
        .then(
          (ab) => new Promise((res, rej) => E.c.decodeAudioData(ab, res, rej)),
        )
        .then((buf) => {
          let pk = 0;
          for (let ch = 0; ch < buf.numberOfChannels; ch++) {
            const d = buf.getChannelData(ch);
            for (let i = 0; i < d.length; i++)
              pk = Math.max(pk, Math.abs(d[i]));
          }
          const target =
            PEAK[name] || (/^motif-/.test(name) ? PEAK.motif : -16);
          samples[name] = { buf, gain: pk ? db(target) / pk : 1 };
        })
        .catch(() => {
          delete samples[name];
        });
    });
  };

  // Film audio ducks the motifs 14 dB: any unmuted video or audio playing.
  const media = () =>
    [...document.querySelectorAll("video, audio")].some(
      (m) => !m.paused && !m.muted && m.volume > 0,
    );
  const setDuck = (v) => {
    ducked = v;
    if (E)
      E.mus.gain.setTargetAtTime(
        v ? db(-14) : 1,
        E.c.currentTime,
        v ? 0.08 : 0.4,
      );
  };
  ["play", "pause", "ended", "volumechange"].forEach((ev) =>
    document.addEventListener(ev, () => setDuck(media()), true),
  );

  const ready = () => {
    if (!E || !on || document.hidden) return false;
    if (E.c.state === "suspended") E.c.resume();
    return true;
  };

  window.score = {
    get on() {
      return on;
    },
    set on(v) {
      on = !!v;
      try {
        sessionStorage.setItem("sound", on ? "on" : "off");
      } catch (e) {
        /* private mode */
      }
      if (E) E.master.gain.setTargetAtTime(on ? 1 : 0, E.c.currentTime, 0.03);
    },
    // Call inside the first click or key. Safe to call again.
    unlock() {
      if (!AC) return;
      if (!E) {
        E = engine(new AC(), true);
        const b = E.c.createBuffer(1, 1, E.c.sampleRate),
          s = E.c.createBufferSource();
        s.buffer = b;
        s.connect(E.c.destination);
        s.start(0);
        setDuck(media());
        load();
      }
      if (E.c.state === "suspended") E.c.resume();
    },
    // opts: at (seconds from now), gain (multiplier), plus per cue:
    // dur (clatter, servo, whoosh), n (flap letters), buffer (tapestop).
    play(name, opts = {}) {
      const cue = C[name];
      if (!cue || !ready()) return;
      const ms = performance.now();
      if (ms - (last[name] || 0) < (cue.gap || 40)) return;
      last[name] = ms;
      const t = E.c.currentTime + 0.01 + (opts.at || 0);
      const s = samples[name];
      if (s) playSample(E, t, s, route(E, {}, opts.gain).sfx);
      else cue.f(route(E, cue, opts.gain), t, opts);
    },
    // The theme on one instrument, once per page view unless opts.again.
    motif(name, opts = {}) {
      if (!M[name] || !ready() || (played[name] && !opts.again)) return false;
      played[name] = true;
      const t = E.c.currentTime + 0.02 + (opts.at || 0),
        s = samples["motif-" + name];
      if (s) playSample(E, t, s, E.mus);
      else motif(E, t, name);
      return true;
    },
    // Which recordings decoded, and whether the motifs are ducked.
    get loaded() {
      return Object.keys(samples).filter((k) => samples[k]);
    },
    get ducked() {
      return ducked;
    },
    // For audio the page cannot see, like a YouTube iframe.
    duck(v) {
      setDuck(!!v || media());
    },
    // Slow a playing video or audio element to a stop, pitch falling with it.
    tapeStop(el, dur = 0.7) {
      return new Promise((res) => {
        if (!el || el.paused) return res();
        const keys = [
          "preservesPitch",
          "mozPreservesPitch",
          "webkitPreservesPitch",
        ].filter((k) => k in el);
        const vol = el.volume,
          t0 = performance.now();
        keys.forEach((k) => {
          el[k] = false;
        });
        const step = () => {
          const p = Math.min(1, (performance.now() - t0) / (dur * 1000));
          el.playbackRate = Math.max(0.0625, Math.pow(0.0625, p));
          el.volume = vol * (p > 0.7 ? (1 - p) / 0.3 : 1);
          if (p < 1) return requestAnimationFrame(step);
          el.pause();
          el.playbackRate = 1;
          el.volume = vol;
          keys.forEach((k) => {
            el[k] = true;
          });
          res();
        };
        requestAnimationFrame(step);
      });
    },
    // Fire a cue or "motif:<instrument>" once, when el is half on screen.
    watch(el, cue, opts) {
      if (typeof el === "string") el = document.querySelector(el);
      if (!el || !window.IntersectionObserver) return;
      const io = new IntersectionObserver(
        ([e]) => {
          if (!e.isIntersecting) return;
          const r = /^motif:/.test(cue)
            ? window.score.motif(cue.slice(6), opts)
            : (window.score.play(cue, opts), true);
          if (r !== false || !on) io.disconnect();
        },
        { threshold: 0.5 },
      );
      io.observe(el);
    },
    cues: Object.keys(C).concat(Object.keys(M).map((k) => "motif:" + k)),
    // Offline render of one cue for tests: resolves to an AudioBuffer.
    render(name, opts = {}, sr = 48000) {
      const mo = /^motif:/.test(name) ? name.slice(6) : null,
        len = mo ? M[mo].len : C[name].len + 0.1;
      const c = new OAC(2, Math.ceil(sr * len), sr),
        X = engine(c, false);
      if (mo) motif(X, 0.05, mo);
      else C[name].f(route(X, C[name], opts.gain), 0.05, opts);
      return c.startRendering
        ? new Promise((res) => {
            const p = c.startRendering();
            if (p && p.then) p.then(res);
            else c.oncomplete = (e) => res(e.renderedBuffer);
          })
        : Promise.reject();
    },
  };
})();
