/* Deck list, deck selection, and the iframe viewer.
   Moved out of app.py's INDEX_HTML with the same behaviour, plus
   window.deckViewer for the tutor panel to read and drive the open deck. */
(function () {
  var list = document.getElementById('deck-list');
  var viewer = document.getElementById('viewer');
  var empty = document.getElementById('empty');

  var decks = [];
  var deckById = {};
  var liById = {};
  var activeDeck = null;
  var changeListeners = [];

  function notifyChange() {
    changeListeners.forEach(function (cb) { cb(); });
  }

  function attachHashListener() {
    try {
      viewer.contentWindow.addEventListener('hashchange', notifyChange);
    } catch (e) {
      /* cross-origin or not-yet-loaded; nothing to attach to */
    }
  }

  document.getElementById('toggle').onclick = function () {
    var opening = document.body.classList.contains('nav-closed');
    document.body.classList.toggle('nav-closed');
    if (opening) document.body.classList.add('tutor-closed');
  };

  function select(deck, li) {
    list.querySelectorAll('li').forEach(function (el) { el.classList.remove('active'); });
    if (li) li.classList.add('active');
    document.body.classList.add('nav-closed');
    empty.hidden = true;
    viewer.hidden = false;
    viewer.src = '/decks/' + deck.id + '/index.html';
    location.hash = deck.id;
    activeDeck = deck;
    notifyChange();
  }

  function current() {
    if (!activeDeck || viewer.hidden) return null;
    var hash;
    try {
      hash = viewer.contentWindow.location.hash;
    } catch (e) {
      return null;
    }
    var m = /^#\/(\d+)/.exec(hash || '');
    // No vertical stacks in these decks: one top-level section per page, build
    // steps as fragments. So the reveal h index is the page index, and the
    // presenter-facing slide number is h + 1.
    return { deck: activeDeck.id, slide: m ? parseInt(m[1], 10) + 1 : 1 };
  }

  function open(deckId, slide) {
    var target = deckById[deckId];
    if (!target) return;
    var hash = '#/' + Math.max(0, (slide || 1) - 1);
    if (activeDeck && activeDeck.id === deckId) {
      try { viewer.contentWindow.location.hash = hash; } catch (e) { /* ignore */ }
      document.body.classList.add('nav-closed');
      return;
    }
    select(target, liById[deckId]);
    viewer.addEventListener('load', function onLoad() {
      viewer.removeEventListener('load', onLoad);
      attachHashListener();
      try { viewer.contentWindow.location.hash = hash; } catch (e) { /* ignore */ }
    });
  }

  function titleOf(deckId) {
    var deck = deckById[deckId];
    return deck ? deck.title : deckId;
  }

  function onChange(cb) {
    changeListeners.push(cb);
  }

  viewer.addEventListener('load', attachHashListener);

  window.deckViewer = { current: current, open: open, titleOf: titleOf, onChange: onChange };

  fetch('/api/decks').then(function (r) { return r.json(); }).then(function (fetched) {
    decks = fetched;
    if (!decks.length) { empty.textContent = 'No decks found.'; return; }
    var initial = null, initialLi = null;
    decks.forEach(function (d) {
      var li = document.createElement('li');
      li.textContent = d.title;
      li.onclick = function () { select(d, li); };
      list.appendChild(li);
      deckById[d.id] = d;
      liById[d.id] = li;
      if (!initial || location.hash.slice(1) === d.id) { initial = d; initialLi = li; }
    });
    select(initial, initialLi);
  }).catch(function () { empty.textContent = 'Failed to load deck list.'; });
})();
