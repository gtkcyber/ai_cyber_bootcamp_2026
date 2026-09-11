/* Graph Analytics for Cyber Security - shared deck runtime.
 *
 * Four jobs, all of them things reveal does not do for us:
 *   1. reading mode  - renders every slide's <aside class="notes"> inline
 *                      under that slide as an ordinary scrolling document.
 *                      Speaker view is a popup that talks to the deck over
 *                      postMessage and needs a web server, so it is dead on
 *                      file:// - which is the whole distribution model.
 *   2. reveal-a11y   - off-screen slides otherwise stay in the DOM,
 *                      tab-focusable and readable by assistive tech.
 *                      Registered after init so it runs on markdown output
 *                      rather than on the raw <textarea>.
 *   3. dark toggle   - best-effort for the cold reader. Visuals are drawn
 *                      for light and will look wrong.
 *   4. overflow guard - reveal scales a fixed canvas and does not reflow, so
 *                      a slide taller than the canvas is silently clipped at
 *                      the bottom edge. Nothing warns you. This measures every
 *                      slide against the canvas and says so, loudly.
 *
 * Call CourseDeck.start(revealOptions) after the reveal scripts have loaded.
 */
window.CourseDeck = (function () {
  'use strict';

  var ASSETS = null;   // resolved from the <script> tag that loaded this file
  var reading = false;
  var built = false;
  var canvas = { w: 1600, h: 900 };
  var guardOn = true;

  (function resolveAssets() {
    var s = document.currentScript;
    if (s && s.src) { ASSETS = s.src.replace(/deck\.js(\?.*)?$/, ''); }
    else { ASSETS = '../assets/'; }
  })();

  /* ------------------------------------------------------------ chrome */

  function button(label, title, onClick) {
    var b = document.createElement('button');
    b.type = 'button';
    b.textContent = label;
    b.title = title;
    b.setAttribute('aria-pressed', 'false');
    b.addEventListener('click', function () { onClick(b); });
    return b;
  }

  function mountTools() {
    var bar = document.createElement('div');
    bar.id = 'deck-tools';

    var readBtn = button('Reading mode', 'Show the notes under every slide (R)', function (b) {
      setReading(!reading, b);
    });
    readBtn.id = 'btn-reading';

    var darkBtn = button('Dark', 'Switch to a dark background', function (b) {
      var on = document.documentElement.getAttribute('data-theme') === 'dark';
      document.documentElement.setAttribute('data-theme', on ? 'light' : 'dark');
      b.setAttribute('aria-pressed', String(!on));
    });

    bar.appendChild(readBtn);
    bar.appendChild(darkBtn);
    document.body.appendChild(bar);

    var warn = document.createElement('div');
    warn.id = 'deck-overflow-banner';
    warn.setAttribute('role', 'status');
    document.body.appendChild(warn);

    var host = document.createElement('div');
    host.id = 'reading';
    document.body.appendChild(host);
  }

  /* ------------------------------------------------------ reading mode */

  // A slide's real content lives inside .accessibilityWrapper once
  // reveal-a11y has run, and directly on the <section> before that.
  function contentOf(section) {
    return section.querySelector(':scope > .accessibilityWrapper') || section;
  }

  function renderSlide(section, isSub, root) {
    var src = contentOf(section);
    var clone = src.cloneNode(true);

    // Notes come out of the clone and get their own block underneath.
    Array.prototype.forEach.call(clone.querySelectorAll('aside.notes'), function (n) {
      n.parentNode.removeChild(n);
    });
    // Presenter cues are stripped from the slide body too, not only from the
    // notes. Where a cue lands depends on how the markdown plugin splits the
    // Note: block, and a cue that slipped into the body would render on the
    // student's copy AND on the slide itself. Strip in both places so it
    // cannot matter which way the parse went.
    Array.prototype.forEach.call(clone.querySelectorAll('.cue'), function (c) {
      c.parentNode.removeChild(c);
    });
    // Fragments are a presentation-pace device. Reading has no pace.
    Array.prototype.forEach.call(clone.querySelectorAll('.fragment'), function (f) {
      f.classList.remove('fragment', 'visible', 'current-fragment');
      f.removeAttribute('data-fragment-index');
    });
    // Reveal swaps data-src for src only on slides it is showing, and the
    // reading copy is never shown by reveal, so its movies and embeds get
    // their sources here. preload="none" and loading="lazy" on the elements
    // keep that from fetching anything until it is played or scrolled to.
    Array.prototype.forEach.call(clone.querySelectorAll('.media[data-src]'), function (m) {
      m.setAttribute('src', m.getAttribute('data-src'));
      m.removeAttribute('data-src');
    });

    var article = document.createElement('article');
    article.className = 'r-slide' + (isSub ? ' r-sub' : '');

    var glass = document.createElement('div');
    glass.className = 'r-glass';
    glass.innerHTML = clone.innerHTML;

    // The headline belongs to the section, not to the glass box.
    var head = glass.querySelector('h1, h2, h3');
    if (head) { article.appendChild(head); }
    if (glass.textContent.trim() || glass.querySelector('svg, table, img, video, iframe')) {
      article.appendChild(glass);
    }

    var note = src.querySelector('aside.notes');
    var body = document.createElement('div');
    body.className = 'r-notes';
    if (note && note.innerHTML.trim()) {
      // The notes carry two audiences. Explanation is written for the student
      // reading cold; anything marked .cue is for whoever is standing up —
      // timings, what to ask the room, where people get stuck. Speaker view
      // shows both because both live inside aside.notes; reading mode must
      // show only the first. Strip on a CLONE so the live DOM that speaker
      // view reads is never touched.
      var shown = note.cloneNode(true);
      Array.prototype.forEach.call(shown.querySelectorAll('.cue'), function (c) {
        c.parentNode.removeChild(c);
      });
      body.innerHTML = shown.innerHTML.trim()
        ? shown.innerHTML
        : '<p class="r-nonote">No notes on this slide yet.</p>';
    } else {
      body.innerHTML = '<p class="r-nonote">No notes on this slide yet.</p>';
    }
    article.appendChild(body);

    root.appendChild(article);
  }

  function buildReading() {
    var root = document.getElementById('reading');
    root.innerHTML = '';
    var tops = document.querySelectorAll('.reveal .slides > section');
    Array.prototype.forEach.call(tops, function (top) {
      var subs = top.querySelectorAll(':scope > section');
      if (subs.length) {
        Array.prototype.forEach.call(subs, function (sub, i) {
          renderSlide(sub, i > 0, root);
        });
      } else {
        renderSlide(top, false, root);
      }
    });
    built = true;
  }

  function setReading(on, btn) {
    if (on && !built) { buildReading(); }
    reading = on;
    document.body.classList.toggle('reading-mode', on);
    if (on) { banner(''); }   // reading mode has no canvas to overflow
    if (btn) {
      btn.setAttribute('aria-pressed', String(on));
      btn.textContent = on ? 'Slides' : 'Reading mode';
    }
    if (window.Reveal && Reveal.isReady && Reveal.isReady()) {
      Reveal.configure({ keyboard: !on });
    }
    if (on) { window.scrollTo(0, 0); }
  }

  /* ----------------------------------------------------- overflow guard */

  // Every slide with no child section: the things a viewer actually lands on.
  function leafSlides() {
    return Array.prototype.filter.call(
      document.querySelectorAll('.reveal .slides section'),
      function (s) { return !s.querySelector(':scope > section'); }
    );
  }

  function labelOf(section) {
    var h = section.querySelector('h1, h2, h3');
    return h ? h.textContent.trim() : '(no heading)';
  }

  // Measuring an off-screen slide is the whole difficulty. Reveal hides
  // inactive slides with display:none, and reveal-a11y hides their content
  // wrapper on top of that, so an element inside a hidden vertical stack has
  // no box at all and reports a height of zero. A guard that trusts that
  // number reports a clean deck while slides clip - which is exactly the bug
  // this function exists to catch. So force the whole ancestor chain visible,
  // measure, and put every inline style back the way it was.
  function measure(section) {
    var saved = [];
    function force(el) {
      saved.push([el, el.getAttribute('style')]);
      el.style.cssText += ';display:block;visibility:visible;opacity:1;' +
                          'position:relative;top:auto;left:auto;height:auto;';
    }
    var node = section;
    while (node && node.tagName === 'SECTION') {
      force(node);
      node = node.parentNode;
    }
    var wrap = section.querySelector(':scope > .accessibilityWrapper');
    if (wrap) { force(wrap); }

    var box = { h: section.scrollHeight, w: section.scrollWidth };

    saved.forEach(function (pair) {
      if (pair[1] === null) { pair[0].removeAttribute('style'); }
      else { pair[0].setAttribute('style', pair[1]); }
    });
    return box;
  }

  // The limit is the configured canvas, not the canvas minus the margin:
  // `margin` is viewport space around the scaled canvas, so it costs the deck
  // nothing internally. Anything past the canvas is clipped rather than shrunk.
  function audit() {
    return leafSlides().map(function (s, i) {
      var box = measure(s);
      return {
        index: i + 1,
        label: labelOf(s),
        height: box.h,
        width: box.w,
        over: box.h > canvas.h || box.w > canvas.w,
        section: s
      };
    });
  }

  function banner(text) {
    var el = document.getElementById('deck-overflow-banner');
    if (!el) { return; }
    el.textContent = text || '';
    el.classList.toggle('on', !!text);
  }

  function runGuard() {
    var rows = audit();
    rows.forEach(function (r) { r.section.dataset.overflow = r.over ? '1' : ''; });

    var bad = rows.filter(function (r) { return r.over; });
    var bar = document.getElementById('deck-tools');
    var pill = document.getElementById('overflow-count');
    if (bad.length && bar && !pill) {
      pill = document.createElement('button');
      pill.id = 'overflow-count';
      pill.type = 'button';
      pill.className = 'overflow-count';
      pill.disabled = true;
      bar.insertBefore(pill, bar.firstChild);
    }
    if (pill) {
      pill.textContent = bad.length + (bad.length === 1 ? ' slide clips' : ' slides clip');
      pill.style.display = bad.length ? '' : 'none';
    }

    if (bad.length) {
      console.warn('[deck] ' + bad.length + ' of ' + rows.length +
                   ' slides overflow the ' + canvas.w + ' x ' + canvas.h +
                   ' canvas and will be clipped:');
      bad.forEach(function (r) {
        console.warn('  slide ' + r.index + '  "' + r.label + '"  ' +
                     'content ' + r.height + 'px tall, ' + r.width + 'px wide');
      });
      console.warn('[deck] cut the slide or move the words into the notes. ' +
                   'Shrinking type is not the fix; the size floors are in SLIDES-PLAN.md.');
    }
    return rows;
  }

  /* --------------------------------------------------------------- a11y */

  function loadA11y() {
    return new Promise(function (resolve) {
      var s = document.createElement('script');
      s.src = ASSETS + 'reveal-a11y/helper.js';
      s.onload = resolve;
      s.onerror = resolve;   // an unstyled deck beats a blank one
      document.body.appendChild(s);
    });
  }

  /* -------------------------------------------------------------- start */

  function start(options) {
    guardOn = !/[?&]guard=0\b/.test(window.location.search);
    var opts = Object.assign({
      width: 1600,
      height: 900,
      margin: 0,
      hash: true,
      slideNumber: 'c/t',
      transition: 'fade',
      transitionSpeed: 'fast',
      // Iframes lazy-load on visibility and we leave it that way: eager
      // loading would open every embed in a module deck at once.
      plugins: [ RevealMarkdown, RevealHighlight, RevealNotes ]
    }, options || {});

    canvas = { w: opts.width, h: opts.height };

    return Reveal.initialize(opts).then(function () {
      return loadA11y();
    }).then(function () {
      mountTools();
      // ?reading=1 opens straight into the document view, so a link can be
      // handed to somebody who wants the notes and not the performance.
      if (/[?&]reading=1\b/.test(window.location.search)) {
        setReading(true, document.getElementById('btn-reading'));
      }
      // On by default. What the guard catches is invisible by construction,
      // since the clipped words are below the fold and nothing marks their
      // absence, so the default has to be loud. A deck that is clean never
      // shows it, and ?guard=0 silences it for a room.
      if (guardOn) {
        runGuard();
        var checkCurrent = function () {
          var s = Reveal.getCurrentSlide();
          if (!s || reading) { banner(''); return; }
          var box = measure(s);
          if (box.h > canvas.h || box.w > canvas.w) {
            banner('This slide overflows the canvas and is clipped: content ' +
                   box.h + ' x ' + box.w + ' in a ' + canvas.h + ' x ' + canvas.w + ' canvas');
            console.warn('[deck] "' + labelOf(s) + '" overflows: content ' +
                         box.h + 'px tall in a ' + canvas.h + 'px canvas');
          } else {
            banner('');
          }
        };
        Reveal.on('slidechanged', checkCurrent);
        checkCurrent();
      }
      document.addEventListener('keydown', function (e) {
        if (e.key !== 'r' && e.key !== 'R') { return; }
        if (e.metaKey || e.ctrlKey || e.altKey) { return; }
        e.preventDefault();
        setReading(!reading, document.getElementById('btn-reading'));
      });
    });
  }

  // audit() is exported so a headless check can measure a deck without a
  // human looking at it. Returns one row per slide; `over` is the verdict.
  return { start: start, audit: audit, runGuard: runGuard };
})();
