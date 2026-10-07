(function () {
  'use strict';
  document.documentElement.classList.add('js');

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
  const pad2 = (n) => String(n).padStart(2, '0');
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const isMobile = () => window.innerWidth <= 760;

  /* ======================================================================
     THE EXHIBIT
     ====================================================================== */
  const ITEMS = window.AMI_GALLERY || [];
  const FIELDS = window.AMI_FIELDS || [];
  const exhibit = $('#exhibit');
  const stage = $('[data-stage]');
  const platesEl = $('[data-plates]');
  const recordInner = $('[data-record-inner]');
  const toggle = $('.reveal-toggle');
  const caption = $('[data-caption]');
  const capHour = $('[data-cap-hour]');
  const capWorld = $('[data-cap-world]');
  const capTitle = $('[data-cap-title]');
  const countNow = $('[data-count-now]');
  const countAll = $('[data-count-all]');
  const dayline = $('[data-dayline]');

  let index = 0;
  let recordOn = false;
  let pinned = false;
  let suppressHover = false;
  let busy = false;
  const plates = [];

  countAll.textContent = pad2(ITEMS.length);

  ITEMS.forEach((item, i) => {
    const el = document.createElement('div');
    el.className = 'plate';
    el.hidden = i !== 0;
    el.style.width = item.w + 'px';
    el.style.height = item.h + 'px';
    const img = document.createElement('img');
    img.alt = item.alt;
    img.width = item.w; img.height = item.h;
    img.decoding = 'async';
    if (i === 0) { img.src = item.src; img.fetchPriority = 'high'; }
    el.appendChild(img);
    platesEl.appendChild(el);
    plates.push({ el, img, item });
  });

  const fileTag = document.createElement('p');
  fileTag.className = 'plate__file';
  stage.appendChild(fileTag);

  // day line ticks
  const track = $('.dayline__track', dayline);
  const ticks = ITEMS.map((item, i) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'tick';
    b.style.left = ((item.h24 - 7) / 15 * 100) + '%';
    b.setAttribute('aria-label', item.hour + ' · ' + item.title);
    b.innerHTML = '<span class="tick__tip">' + esc(item.hour + ' · ' + item.title) + '</span>';
    b.addEventListener('click', () => go(i));
    dayline.insertBefore(b, track.nextSibling);
    return b;
  });

  function ensureSrc(i) {
    const p = plates[(i + ITEMS.length) % ITEMS.length];
    if (!p.img.src) p.img.src = p.item.src;
    return p;
  }

  // Where a plate sits: full-bleed in the gallery, mounted as a specimen in the record.
  function geometry(item) {
    const W = stage.clientWidth, H = stage.clientHeight;
    const ar = item.w / item.h;
    if (!recordOn) {
      const cover = Math.abs(Math.log(ar / (W / H))) < 0.42;
      if (cover) {
        const s = Math.max(W / item.w, H / item.h);
        return { s, x: (W - item.w * s) / 2, y: (H - item.h * s) / 2 };
      }
      const s = isMobile()
        ? Math.min(W / item.w, (H * 0.66) / item.h)
        : Math.min((W * 0.84) / item.w, (H * 0.76) / item.h);
      return { s, x: (W - item.w * s) / 2, y: (H * (isMobile() ? 0.42 : 0.46)) - (item.h * s) / 2 };
    }
    let box;
    if (isMobile()) {
      box = { x: 16, y: 60, w: W - 32, h: H * 0.36 - 72 };
    } else {
      const g = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--gutter')) || 32;
      const panel = Math.min(W * 0.42, 620);
      const left = g + 56;
      box = { x: left, y: H * 0.13, w: W - panel - g - left - Math.max(40, W * 0.04), h: H * 0.66 };
    }
    const s = Math.min(box.w / item.w, box.h / item.h);
    return { s, x: box.x + (box.w - item.w * s) / 2, y: box.y + (box.h - item.h * s) / 2 };
  }

  function place(p, extra) {
    const g = geometry(p.item);
    let { s, x, y } = g;
    if (extra) {
      const k = extra.k || 1;
      x -= (k - 1) * p.item.w * s / 2; y -= (k - 1) * p.item.h * s / 2; s *= k;
      x += extra.dx || 0;
    }
    p.el.style.transform = 'translate3d(' + x + 'px,' + y + 'px,0) scale(' + s + ')';
    return g;
  }

  function placeFile() {
    const p = plates[index];
    if (!recordOn || !p.item.file) { fileTag.textContent = ''; return; }
    const g = geometry(p.item);
    fileTag.textContent = p.item.file;
    fileTag.style.left = g.x + 'px';
    fileTag.style.top = (g.y + p.item.h * g.s) + 'px';
  }

  function layout() {
    plates.forEach((p, i) => { if (i === index) place(p); });
    placeFile();
  }

  function setCaption(item, animate) {
    const apply = () => {
      capHour.textContent = item.hour;
      capWorld.textContent = item.world + ' · ' + item.worldName;
      capTitle.textContent = item.title;
      countNow.textContent = pad2(index + 1);
      exhibit.style.setProperty('--echo', item.echo.ink);
      ticks.forEach((t, i) => t.setAttribute('aria-current', i === index ? 'true' : 'false'));
    };
    if (!animate || reduced) { apply(); return; }
    caption.classList.add('is-swapping');
    setTimeout(() => { apply(); caption.classList.remove('is-swapping'); }, 380);
  }

  function renderRecord(item) {
    const f = item.fields || {};
    let n = 0;
    const idx = () => ' style="--i:' + (n++) + '"';
    const meta = [item.hour, item.channel && ('Channel: ' + item.channel), item.audience && ('For: ' + item.audience)].filter(Boolean);
    let html = '';
    html += '<div class="record__head"' + idx() + '>';
    html += '<p class="label record__kicker">' + esc(item.world + ' · ' + item.worldName + ' · ' + item.pillar) + '</p>';
    html += '<h2 class="record__title">' + esc(item.title) + '</h2>';
    html += '<p class="record__meta">' + meta.map((m) => '<span>' + esc(m) + '</span>').join('') + '</p>';
    html += '</div>';
    const promptGap = !f.prompt;
    html += '<dl class="record__prompt' + (promptGap ? ' is-gap' : '') + '"' + idx() + '><dt class="label">Final generation prompt</dt><dd>' + (promptGap ? 'Not yet recorded' : esc(f.prompt)) + '</dd></dl>';
    html += '<dl class="record__grid">';
    FIELDS.forEach(([key, label]) => {
      if (key === 'prompt') return;
      const v = f[key];
      const wide = key === 'params' || key === 'location' || key === 'style' || key === 'colour' || key === 'model';
      const gap = v == null;
      let dd;
      if (gap) dd = 'Not yet recorded';
      else if (typeof v === 'object') dd = esc(v.v) + (v.note ? '<small>' + esc(v.note) + '</small>' : '');
      else dd = esc(v);
      html += '<div class="' + (wide ? 'is-wide ' : '') + (gap ? 'is-gap' : '') + '"' + idx() + '><dt>' + esc(label) + '</dt><dd>' + dd + '</dd></div>';
    });
    html += '</dl>';
    html += '<p class="record__foot"' + idx() + '>Values come from the presentation. Fields marked “not yet recorded” are not documented there yet.</p>';
    html += '<button type="button" class="record__close"' + idx() + '>Back to the image</button>';
    recordInner.innerHTML = html;
    $('.record__close', recordInner).addEventListener('click', () => { pinned = false; setRecord(false, true); });
  }

  function setRecord(on, fromUser) {
    if (on === recordOn) return;
    recordOn = on;
    if (on) renderRecord(ITEMS[index]);
    exhibit.classList.toggle('is-record', on);
    toggle.setAttribute('aria-pressed', on ? 'true' : 'false');
    if (!on && fromUser) suppressHover = true;
    layout();
  }

  function go(next, dir) {
    next = (next + ITEMS.length) % ITEMS.length;
    if (next === index || busy) return;
    if (dir === undefined) dir = next > index ? 1 : -1;
    const from = plates[index];
    const to = ensureSrc(next);
    ensureSrc(next + 1); ensureSrc(next - 1);
    index = next;

    const T = reduced ? 0 : 1100;
    busy = !reduced;
    to.el.hidden = false;
    to.el.style.transition = 'none';
    to.el.style.zIndex = 2;
    from.el.style.zIndex = 1;
    place(to, { k: 1.06 });
    to.el.style.clipPath = dir > 0 ? 'inset(0 0 0 100%)' : 'inset(0 100% 0 0)';
    to.el.style.opacity = '1';
    to.el.getBoundingClientRect();
    to.el.style.transition = '';
    to.el.classList.add('is-entering');
    requestAnimationFrame(() => {
      to.el.style.clipPath = 'inset(0 0 0 0)';
      place(to);
      from.el.classList.add('is-leaving');
      place(from, { dx: -dir * stage.clientWidth * 0.06 });
    });

    setCaption(to.item, true);
    if (recordOn) {
      recordInner.style.opacity = '0';
      setTimeout(() => { renderRecord(to.item); recordInner.style.opacity = ''; placeFile(); }, reduced ? 0 : 260);
    }
    placeFile();

    setTimeout(() => {
      from.el.hidden = true;
      from.el.classList.remove('is-leaving');
      from.el.style.opacity = '';
      to.el.classList.remove('is-entering');
      to.el.style.clipPath = '';
      busy = false;
    }, T + 40);
  }

  // initial state
  plates[0].el.classList.add('is-active');
  setCaption(ITEMS[0], false);
  ensureSrc(1); ensureSrc(-1);
  recordInner.style.transition = 'opacity .25s ease';
  layout();
  window.addEventListener('resize', () => { layout(); }, { passive: true });

  $('[data-next]').addEventListener('click', () => go(index + 1, 1));
  $('[data-prev]').addEventListener('click', () => go(index - 1, -1));

  toggle.addEventListener('click', () => {
    if (recordOn) { pinned = false; setRecord(false, true); }
    else { pinned = true; setRecord(true, true); }
  });

  // hover reveal (pointer devices)
  let hoverTimer = 0;
  const zone = $('[data-hover-zone]');
  zone.addEventListener('pointerenter', (e) => {
    if (e.pointerType !== 'mouse' || suppressHover) return;
    clearTimeout(hoverTimer);
    hoverTimer = setTimeout(() => setRecord(true), 420);
  });
  zone.addEventListener('pointerleave', () => { clearTimeout(hoverTimer); suppressHover = false; });
  exhibit.addEventListener('pointerleave', (e) => {
    if (e.pointerType !== 'mouse') return;
    clearTimeout(hoverTimer);
    suppressHover = false;
    if (!pinned) setRecord(false);
  });
  // clicking the mounted plate returns to the full image
  stage.addEventListener('click', (e) => {
    if (e.target.closest('button, a, .record')) return;
    if (finePointer.matches) {
      if (recordOn) { pinned = false; setRecord(false, true); }
      else { pinned = true; setRecord(true, true); }
    }
  });

  // touch: tap toggles the record, swipe navigates
  let sx = 0, sy = 0, st = 0, touching = false;
  stage.addEventListener('pointerdown', (e) => {
    if (e.pointerType === 'mouse') return;
    touching = true; sx = e.clientX; sy = e.clientY; st = Date.now();
  });
  stage.addEventListener('pointerup', (e) => {
    if (!touching || e.pointerType === 'mouse') return;
    touching = false;
    if (e.target.closest('button, a, .record')) return;
    const dx = e.clientX - sx, dy = e.clientY - sy;
    if (Math.abs(dx) > 48 && Math.abs(dx) > Math.abs(dy) * 1.3) { go(index + (dx < 0 ? 1 : -1), dx < 0 ? 1 : -1); return; }
    if (Math.abs(dx) < 10 && Math.abs(dy) < 10 && Date.now() - st < 500) {
      pinned = !recordOn; setRecord(!recordOn, true);
    }
  });
  stage.addEventListener('pointercancel', () => { touching = false; });

  // keyboard, while the exhibit is on screen
  let exhibitVisible = true;
  new IntersectionObserver((en) => { exhibitVisible = en[0].isIntersecting && en[0].intersectionRatio > 0.5; }, { threshold: [0, 0.5, 1] }).observe(exhibit);
  document.addEventListener('keydown', (e) => {
    if (!exhibitVisible || e.metaKey || e.ctrlKey || e.altKey) return;
    const t = e.target;
    if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
    if (e.key === 'ArrowRight') { e.preventDefault(); go(index + 1, 1); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); go(index - 1, -1); }
    else if (e.key === 'i' || e.key === 'I') { pinned = !recordOn; setRecord(!recordOn, true); }
    else if (e.key === 'Escape' && recordOn) { pinned = false; setRecord(false, true); }
  });

  /* ======================================================================
     CHAPTER RAIL
     ====================================================================== */
  const rail = $('[data-rail]');
  const railLinks = $$('a', rail);
  railLinks.forEach((a) => { a.innerHTML = '<span>' + a.textContent + '</span>'; });
  const chapterIds = railLinks.map((a) => a.getAttribute('href').slice(1));
  const chapterEls = chapterIds.map((id) => document.getElementById(id)).filter(Boolean);
  function updateRail() {
    const y = window.scrollY, vh = window.innerHeight;
    const closeTop = $('#ownership').getBoundingClientRect().top;
    const dirTop = $('#direction').getBoundingClientRect().top;
    rail.classList.toggle('is-on', dirTop < vh * 0.6 && closeTop > vh * 0.5);
    let current = null;
    chapterEls.forEach((el) => { if (el.getBoundingClientRect().top < vh * 0.45) current = el.id; });
    railLinks.forEach((a) => a.setAttribute('aria-current', a.getAttribute('href') === '#' + current ? 'true' : 'false'));
    const onPaper = current === 'prompt' && $('#prompt').getBoundingClientRect().bottom > vh * 0.5;
    rail.classList.toggle('on-paper', onPaper);
    return y;
  }

  /* ======================================================================
     WORLDS (day strip)
     ====================================================================== */
  const worlds = $$('[data-worlds] .world');
  const openWorld = (w) => worlds.forEach((x) => x.classList.toggle('is-open', x === w));
  worlds.forEach((w) => {
    w.addEventListener('click', () => openWorld(w));
    w.addEventListener('focus', () => openWorld(w));
    w.addEventListener('keydown', (e) => {
      const i = worlds.indexOf(w);
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); worlds[(i + 1) % worlds.length].focus(); }
      if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { e.preventDefault(); worlds[(i - 1 + worlds.length) % worlds.length].focus(); }
    });
    let t = 0;
    w.addEventListener('pointerenter', (e) => { if (e.pointerType === 'mouse' && !isMobile()) { t = setTimeout(() => openWorld(w), 160); } });
    w.addEventListener('pointerleave', () => clearTimeout(t));
  });

  /* ======================================================================
     DRAG-SCROLL rows (mouse)
     ====================================================================== */
  $$('[data-drag-scroll]').forEach((row) => {
    let down = false, startX = 0, startL = 0, moved = false;
    row.addEventListener('pointerdown', (e) => {
      if (e.pointerType !== 'mouse') return;
      down = true; moved = false; startX = e.clientX; startL = row.scrollLeft;
    });
    window.addEventListener('pointermove', (e) => {
      if (!down) return;
      const dx = e.clientX - startX;
      if (Math.abs(dx) > 4) { moved = true; row.classList.add('is-dragging'); }
      row.scrollLeft = startL - dx;
    });
    window.addEventListener('pointerup', () => { down = false; row.classList.remove('is-dragging'); });
    row.addEventListener('click', (e) => { if (moved) { e.preventDefault(); e.stopPropagation(); } }, true);
  });

  /* ======================================================================
     COMPARE slider
     ====================================================================== */
  $$('[data-compare]').forEach((c) => {
    const r = $('.compare__range', c);
    const set = () => c.style.setProperty('--pos', r.value + '%');
    r.addEventListener('input', set); set();
  });

  /* ======================================================================
     NINE-PART PROMPT (paper chapter)
     ====================================================================== */
  const nine = $('[data-nine]');
  if (nine) {
    const prompt = $('.prompt-text', nine);
    const parts = $$('[data-part]', nine);
    const light = (key) => {
      parts.forEach((p) => p.classList.toggle('is-on', p.dataset.part === key));
      prompt.classList.toggle('is-focus', !!key);
      $$('[data-seg]', prompt).forEach((s) => s.classList.toggle('is-on', s.dataset.seg === key));
    };
    parts.forEach((p) => {
      p.tabIndex = 0;
      p.addEventListener('pointerenter', () => light(p.dataset.part));
      p.addEventListener('focus', () => light(p.dataset.part));
      p.addEventListener('click', () => light(p.dataset.part));
    });
    $('.nine__parts', nine).addEventListener('pointerleave', () => light(null));
    $('.nine__parts', nine).addEventListener('focusout', (e) => { if (!nine.contains(e.relatedTarget)) light(null); });
  }

  /* ======================================================================
     ANATOMY: the eight-layer system
     ====================================================================== */
  const LAYERS = {
    moment: {
      value: 'Golden hour promenade',
      rule: 'One moment from the 42-shot matrix: world, moment, setting, cast, time, shot, format and use, locked before anything is generated.',
      fixed: 'W04 · Waterfront · Mid-stride, mid-laugh',
      segs: ['scene', 'subject'], zoom: [1, 50, 50]
    },
    direction: {
      value: 'Unhurried, warm',
      rule: 'Directed from your brand book. A direction guide and the 42-shot matrix turn An Exceptional Address into One Exceptional Day, approved at G2 before generation.',
      fixed: 'Mood is one of the nine prompt parts',
      segs: ['mood'], zoom: [1.04, 50, 50]
    },
    cast: {
      value: 'Couple, 30s',
      rule: 'Drawn from the locked cast bank: 24 AI characters, character sheets approved at G1. Wardrobe comes from culturally reviewed briefs.',
      fixed: 'Styling: linen, understated · Cultural context: modest, contemporary UAE',
      segs: ['subject', 'styling', 'culture'], zoom: [1.55, 46, 42]
    },
    environment: {
      value: 'Waterfront promenade',
      rule: 'A real place on the island, matched to a recce reference. The promenade, railing, paving and palms, and the real sightline to the towers, are kept. Nothing is invented.',
      fixed: '49 settings across six worlds',
      segs: ['environment', 'scene'], zoom: [1.12, 80, 55]
    },
    light: {
      value: '17:30 · low sun, backlit',
      rule: 'Light true to the hour: sun, shadows and reflections consistent with the time and the view.',
      fixed: 'Long shadows across the paving, sun between the towers',
      segs: ['lighting'], zoom: [1.6, 68, 28]
    },
    photography: {
      value: '35mm · eye level · f/4 · 3:2',
      rule: 'Every prompt reads like a photographer’s shot list. The read, framing and format are set per shot; natural skin and fine grain hold for the whole library.',
      fixed: 'Framing: medium-wide · Texture: fine grain · Output: 3:2 master',
      segs: ['camera', 'finish', 'output'], zoom: [1, 50, 50]
    },
    generation: {
      value: 'Omni · people & lifestyle route',
      rule: 'Generated in waves on Omni across 40+ models, locked to the cast sheet, the wardrobe brief and the W04 promenade reference. Model, version, seed and settings go on record for every asset.',
      fixed: 'Excluded: text, signage, logos, waxy skin, distorted hands · Model, version and seed: not yet recorded',
      segs: [], zoom: [1, 50, 50]
    },
    craft: {
      value: 'Best three → one master',
      rule: 'Explore wide, select ruthlessly. Then inpainting, retouch, one colour grade and four QA gates. On this frame: inpainting on hands and fabric, retouch on signage.',
      fixed: 'Rounds R1–R4 · approved at G5',
      segs: [], zoom: [2.1, 47, 72]
    }
  };
  const anatomy = $('[data-anatomy]');
  if (anatomy) {
    const panel = $('[data-anatomy-panel]', anatomy);
    const prompt = $('[data-anatomy-prompt]', anatomy);
    const img = $('.anatomy__frame img', anatomy);
    const tabs = $$('[data-layer]', anatomy);
    const select = (key, focus) => {
      const L = LAYERS[key];
      tabs.forEach((t) => { const on = t.dataset.layer === key; t.setAttribute('aria-selected', on ? 'true' : 'false'); t.tabIndex = on ? 0 : -1; if (on && focus) t.focus(); });
      panel.innerHTML = '<p class="a-value">' + esc(L.value) + '</p><p class="a-rule">' + esc(L.rule) + '</p><p class="a-fixed">' + esc(L.fixed) + '</p>';
      prompt.classList.toggle('is-focus', L.segs.length > 0);
      $$('[data-seg]', prompt).forEach((s) => s.classList.toggle('is-on', L.segs.includes(s.dataset.seg)));
      const [z, ox, oy] = L.zoom;
      img.style.transformOrigin = ox + '% ' + oy + '%';
      img.style.transform = 'scale(' + z + ')';
    };
    tabs.forEach((t, i) => {
      t.addEventListener('click', () => select(t.dataset.layer));
      t.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowDown' || e.key === 'ArrowRight') { e.preventDefault(); select(tabs[(i + 1) % tabs.length].dataset.layer, true); }
        if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') { e.preventDefault(); select(tabs[(i - 1 + tabs.length) % tabs.length].dataset.layer, true); }
      });
    });
    select('moment');
  }

  /* ======================================================================
     CONFIGURATOR: 1 moment → 207,360+ combinations
     ====================================================================== */
  const SETTINGS = [
    { key: 'cast', label: 'Cast', x: 8, opts: ['Couple', 'Friends', 'Family', 'Colleagues', 'Visitors'], def: 0 },
    { key: 'wardrobe', label: 'Wardrobe', x: 3, opts: ['Emirati', 'Modest contemporary', 'Smart casual'], def: 0 },
    { key: 'action', label: 'Action', x: 6, opts: ['Arriving', 'Walking', 'Turning', 'Talking', 'Laughing'], def: 1 },
    { key: 'shot', label: 'Shot size', x: 6, opts: ['Establishing', 'Wide', 'Medium', 'Close-up', 'Detail'], def: 1 },
    { key: 'angle', label: 'Angle', x: 4, opts: ['Eye level', 'Low', 'High', 'Over-the-shoulder'], def: 0 },
    { key: 'view', label: 'Viewpoint', x: 4, opts: ['Skyline', 'Waterfront', 'Palms', 'Café terrace'], def: 0 },
    { key: 'light', label: 'Light', x: 3, opts: ['Backlit', 'Side light', 'Front light'], def: 0 },
    { key: 'format', label: 'Format', x: 5, opts: ['3:2', '16:9', '4:5', '9:16', '1:1'], def: 0 }
  ];
  const SHOT = { Establishing: [1, 50, 50], Wide: [1, 50, 50], Medium: [1.45, 47, 40], 'Close-up': [2.4, 46, 30], Detail: [3.1, 47, 72] };
  const config = $('[data-config]');
  if (config) {
    const controls = $('[data-config-controls]', config);
    const frame = $('[data-config-frame]', config);
    const img = $('[data-config-img]', config);
    const brief = $('[data-config-brief]', config);
    const math = $('[data-config-math]', config);
    const count = $('[data-config-count]', config);
    const state = {};
    SETTINGS.forEach((s) => {
      state[s.key] = s.opts[s.def];
      const row = document.createElement('div');
      row.className = 'cfg-row';
      row.setAttribute('role', 'group');
      row.setAttribute('aria-label', s.label);
      row.innerHTML = '<span class="cfg-row__k">' + esc(s.label) + '</span><div class="cfg-row__opts"></div><span class="cfg-row__x">×' + s.x + '+</span>';
      const opts = $('.cfg-row__opts', row);
      s.opts.forEach((o) => {
        const b = document.createElement('button');
        b.type = 'button'; b.className = 'chip'; b.textContent = o;
        b.setAttribute('aria-pressed', o === state[s.key] ? 'true' : 'false');
        b.addEventListener('click', () => {
          state[s.key] = o;
          $$('.chip', opts).forEach((c) => c.setAttribute('aria-pressed', c === b ? 'true' : 'false'));
          renderConfig();
        });
        opts.appendChild(b);
      });
      const more = document.createElement('span');
      more.className = 'chip chip--more'; more.textContent = '…';
      more.setAttribute('aria-hidden', 'true');
      opts.appendChild(more);
      controls.appendChild(row);
    });
    math.innerHTML = SETTINGS.map((s) => '<b>' + s.x + '</b>').join(' × ') + ' =';
    const total = SETTINGS.reduce((a, s) => a * s.x, 1);

    function sizeFrame() {
      const [a, b] = state.format.split(':').map(Number);
      const ar = a / b;
      const maxW = frame.parentElement.clientWidth;
      const maxH = Math.min(window.innerHeight * 0.62, 640);
      const w = Math.min(maxW, maxH * ar);
      frame.style.aspectRatio = a + ' / ' + b;
      frame.style.width = w + 'px';
    }
    function renderConfig() {
      sizeFrame();
      const [z, ox, oy] = SHOT[state.shot];
      img.style.setProperty('--zoom', z);
      img.style.setProperty('--ox', ox + '%');
      img.style.setProperty('--oy', oy + '%');
      const cast = state.cast.toLowerCase();
      brief.textContent = 'Golden hour promenade, 17:30. ' + (cast === 'family' ? 'A family' : cast === 'friends' ? 'Friends' : cast === 'colleagues' ? 'Colleagues' : cast === 'visitors' ? 'Visitors' : 'A couple') +
        ', ' + state.wardrobe.toLowerCase() + (state.wardrobe === 'Emirati' ? ' dress' : '') + ', ' + state.action.toLowerCase() + '. ' +
        state.shot + ', ' + state.angle.toLowerCase() + ', ' + state.view.toLowerCase() + ' behind. ' + state.light + '. ' + state.format + '.';
    }
    renderConfig();
    window.addEventListener('resize', sizeFrame, { passive: true });

    let counted = false;
    new IntersectionObserver((en) => {
      if (!en[0].isIntersecting || counted) return;
      counted = true;
      if (reduced) { count.textContent = total.toLocaleString('en-US'); return; }
      const t0 = performance.now(), D = 1800;
      const tick = (t) => {
        const k = clamp((t - t0) / D, 0, 1);
        const e = 1 - Math.pow(1 - k, 4);
        count.textContent = Math.round(1 + (total - 1) * e).toLocaleString('en-US');
        if (k < 1) requestAnimationFrame(tick);
      };
      count.textContent = '1';
      requestAnimationFrame(tick);
    }, { threshold: 0.4 }).observe($('.config__total', config));
  }

  /* ======================================================================
     ONE MASTER → EVERY CHANNEL (scroll-scrubbed)
     ====================================================================== */
  const split = $('[data-split]');
  if (split) {
    const box = $('[data-channels]', split);
    const frames = $$('.ch', box);
    const countEl = $('[data-split-count]', split);
    const MASTER_AR = 1672 / 941;
    const ar = (el) => { const [a, b] = getComputedStyle(el).getPropertyValue('--ar').split('/').map(Number); return a / b; };
    // desktop composition, in fractions of the container width
    const WIDE = {
      web: [0, 0, .30], bb: [0, .19, .30], lb: [0, .335, .30], mob: [0, .385, .16],
      print: [.32, 0, .13], adshel: [.47, 0, .13], hp: [.62, 0, .085], story: [.725, 0, .095], feed: [.84, 0, .16],
      crm: [.32, .215, .2], dooh: [.54, .215, .2], mpu: [.76, .215, .1], sq: [.88, .215, .12]
    };
    const FOCUS = { px: '47%', py: '45%' };
    let targets = [], master = null;

    function masonry(W, cols) {
      const gap = 8, cw = (W - gap * (cols - 1)) / cols;
      const h = new Array(cols).fill(0);
      const order = ['web', 'print', 'feed', 'bb', 'story', 'crm', 'adshel', 'sq', 'dooh', 'hp', 'mpu', 'lb', 'mob'];
      const out = {};
      order.forEach((k) => {
        const el = frames.find((f) => f.dataset.ch === k);
        let c = h.indexOf(Math.min(...h));
        const r = ar(el);
        const fh = cw / r;
        out[k] = { x: c * (cw + gap), y: h[c], w: cw, h: fh };
        h[c] += fh + gap + 4;
      });
      return { rects: out, height: Math.max(...h) };
    }

    function computeTargets() {
      const W = box.clientWidth;
      const H = box.parentElement.clientHeight - box.offsetTop - (countEl.offsetHeight + 24);
      box.style.height = Math.max(160, H) + 'px';
      const avail = Math.max(160, H);
      let rects, height;
      if (W > 900) {
        rects = {};
        frames.forEach((f) => {
          const [x, y, w] = WIDE[f.dataset.ch];
          rects[f.dataset.ch] = { x: x * W, y: y * W, w: w * W, h: (w * W) / ar(f) };
        });
        height = 0.41 * W;
      } else {
        const m = masonry(W, W > 560 ? 3 : 2);
        rects = m.rects; height = m.height;
      }
      const k = Math.min(1, avail / height);
      const offX = (W - W * k) / 2;
      targets = frames.map((f) => {
        const r = rects[f.dataset.ch];
        return { x: offX + r.x * k, y: r.y * k, w: r.w * k, h: r.h * k };
      });
      const mw = Math.min(W * 0.7, avail * MASTER_AR * 0.92);
      const mh = mw / MASTER_AR;
      master = { x: (W - mw) / 2, y: Math.max(0, (avail - mh) / 2), w: mw, h: mh };
      frames.forEach((f) => { f.style.setProperty('--px', FOCUS.px); f.style.setProperty('--py', FOCUS.py); });
    }
    const ease = (t) => (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
    function renderSplit() {
      if (!master) return;
      const r = split.getBoundingClientRect();
      const span = split.offsetHeight - window.innerHeight;
      const p = reduced ? 1 : clamp(-r.top / Math.max(1, span), 0, 1);
      let done = 0;
      frames.forEach((f, i) => {
        const local = ease(clamp((p - 0.08 - i * 0.025) / 0.55, 0, 1));
        const t = targets[i];
        const x = master.x + (t.x - master.x) * local;
        const y = master.y + (t.y - master.y) * local;
        const w = master.w + (t.w - master.w) * local;
        const h = master.h + (t.h - master.h) * local;
        f.style.transform = 'translate3d(' + x + 'px,' + y + 'px,0)';
        f.style.width = w + 'px';
        f.style.height = h + 'px';
        f.style.zIndex = String(100 - i);
        f.style.setProperty('--cap', local > 0.96 ? 1 : 0);
        if (local > 0.5) done++;
      });
      countEl.innerHTML = done === 0 ? '<span>1</span> master' : '<span>1</span> master → <span>' + done + '</span> formats';
    }
    computeTargets();
    renderSplit();
    window.addEventListener('resize', () => { computeTargets(); renderSplit(); }, { passive: true });
    window.addEventListener('scroll', renderSplit, { passive: true });
  }

  /* ======================================================================
     SAME SHOT. NEW HOUR.
     ====================================================================== */
  const hour = $('[data-hour]');
  if (hour) {
    const r = $('[data-hour-range]', hour);
    const frames = $('.hour__frames', hour);
    const set = () => frames.style.setProperty('--night', r.value / 100);
    r.addEventListener('input', set); set();
  }

  /* ======================================================================
     Scroll reveals (content is visible without JS)
     ====================================================================== */
  const revealSel = [
    '.threshold__statement', '.bar__text', '.params', '.stakes__risk',
    '.chapter__head', '.idea-chain', '.method', '.split__text', '.recce__text', '.island-rules',
    '.concept-chain', '.matrix', '.nine', '.omni', '.craft__cols', '.gates', '.library__text', '.asset-files',
    '.pipeline__key', '.plan', '.config', '.hour__text', '.elsewhere', '.own .wrap', '.proof__stats', '.close__inner'
  ];
  const maskSel = ['.bar__figure', '.triptych', '.split__media', '.recce__media', '.ref-to-final__pair', '.wardrobe', '.inputs__row', '.wide-figure', '.contact', '.compare', '.library__shot', '.anatomy__frame', '.hour__frames'];
  if (!reduced && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
    revealSel.forEach((s) => $$(s).forEach((el) => { el.setAttribute('data-reveal', ''); io.observe(el); }));
    maskSel.forEach((s) => $$(s).forEach((el) => { el.setAttribute('data-reveal', 'mask'); io.observe(el); }));
  }

  let ticking = false;
  window.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => { updateRail(); ticking = false; });
  }, { passive: true });
  updateRail();
})();
