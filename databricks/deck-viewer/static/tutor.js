/* Tutor panel: history, streamed thread with source chips, composer.

   There is no scope selector here: the tutor has no retrieval index to scope,
   so a question is always about the deck the student has open, or about the
   course at large when none is. */
(function () {
  var API = '/api/tutor';
  var RENDER_INTERVAL_MS = 80;

  var historyBtn = document.getElementById('tutor-history');
  var newBtn = document.getElementById('tutor-new');
  var convList = document.getElementById('tutor-conversations');
  var thread = document.getElementById('tutor-thread');
  var contextLine = document.getElementById('tutor-context');
  var input = document.getElementById('tutor-input');
  var sendBtn = document.getElementById('tutor-send');
  var toggleBtn = document.getElementById('tutor-toggle');

  var conversationId = null;
  var streaming = false;

  // --- in-flight chat request tracking -----------------------------------
  // Exactly one /chat stream is ever "current". New, loading a different
  // conversation, and deleting one all abort whatever is in flight and bump
  // the sequence number, so any frame from a superseded request is ignored
  // even if it arrives after the swap (a late `meta` must never re-attach
  // the old conversation_id to a question the user has since redirected).

  var requestSeq = 0;
  var activeRequest = null; // { seq, cancel }

  function cancelActiveRequest() {
    if (activeRequest) {
      activeRequest.cancel();
      activeRequest = null;
    }
    setStreaming(false);
  }

  // --- panel open/close, mirroring the left nav -------------------------

  toggleBtn.onclick = function () {
    var opening = document.body.classList.contains('tutor-closed');
    document.body.classList.toggle('tutor-closed');
    if (opening) document.body.classList.add('nav-closed');
  };

  // --- context line ------------------------------------------------------
  // The open deck and the presenter-facing slide number, straight from the
  // viewer. There is no backend lookup: every deck is one top-level section
  // per page, so the viewer's own slide number is the right one.

  function updateContext() {
    var cur = window.deckViewer.current();
    if (!cur) {
      contextLine.textContent = 'No deck open. Ask about anything in the course.';
      return;
    }
    contextLine.textContent = 'Context: ' + window.deckViewer.titleOf(cur.deck) + ', slide ' + cur.slide;
  }

  // --- relative time for the conversation list -----------------------------

  function relativeTime(iso) {
    var diffMs = Date.now() - new Date(iso).getTime();
    var mins = Math.round(diffMs / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return mins + ' min ago';
    var hours = Math.round(mins / 60);
    if (hours < 24) return hours + ' hr ago';
    var days = Math.round(hours / 24);
    return days + ' day' + (days === 1 ? '' : 's') + ' ago';
  }

  // --- conversation list ----------------------------------------------------

  historyBtn.onclick = function () {
    convList.hidden = !convList.hidden;
    if (!convList.hidden) refreshConversations();
  };

  newBtn.onclick = function () {
    cancelActiveRequest();
    conversationId = null;
    thread.innerHTML = '';
    input.value = '';
    input.style.height = '';
    convList.hidden = true;
  };

  function refreshConversations() {
    fetch(API + '/conversations').then(function (r) {
      if (!r.ok) throw new Error('conversations request failed');
      return r.json();
    }).then(function (list) {
      convList.innerHTML = '';
      list.forEach(function (c) {
        var li = document.createElement('li');

        var title = document.createElement('span');
        title.className = 'conv-title';
        title.textContent = c.title || 'New conversation';

        var time = document.createElement('span');
        time.className = 'conv-time';
        time.textContent = relativeTime(c.updated);

        var del = document.createElement('button');
        del.type = 'button';
        del.className = 'conv-delete';
        del.setAttribute('aria-label', 'Delete conversation');
        del.textContent = '×';
        del.onclick = function (ev) {
          ev.stopPropagation();
          if (!window.confirm('Delete this conversation?')) return;
          cancelActiveRequest();
          fetch(API + '/conversations/' + c.id, { method: 'DELETE' }).then(function () {
            if (conversationId === c.id) {
              conversationId = null;
              thread.innerHTML = '';
            }
            refreshConversations();
          });
        };

        li.appendChild(title);
        li.appendChild(time);
        li.appendChild(del);
        li.onclick = function () { loadConversation(c.id); };
        convList.appendChild(li);
      });
    }).catch(function () {
      convList.innerHTML = '';
      var li = document.createElement('li');
      li.className = 'conv-error';
      li.textContent = 'Could not load conversations.';
      convList.appendChild(li);
    });
  }

  function loadConversation(id) {
    cancelActiveRequest();
    fetch(API + '/conversations/' + id).then(function (r) { return r.ok ? r.json() : null; }).then(function (conv) {
      if (!conv) return;
      conversationId = conv.id;
      thread.innerHTML = '';
      // conv.scope records which deck the conversation started on. Nothing is
      // restored from it: the context line follows the deck that is open now,
      // and loading an old conversation only replays its messages.
      conv.messages.forEach(function (m) {
        if (m.role === 'user') addUserMessage(m.content);
        else addAssistantMessage(m.content, m.citations || []);
      });
      convList.hidden = true;
    });
  }

  // --- thread rendering -------------------------------------------------
  // marked does not sanitize link/image schemes on its own, so a
  // `javascript:` markdown link in a model answer would otherwise become
  // live. Parse into a detached element first and strip anything that
  // isn't http(s) before it ever reaches the DOM the user can click.

  function sanitizeHtml(html) {
    var container = document.createElement('div');
    container.innerHTML = html;

    container.querySelectorAll('a').forEach(function (a) {
      var href = (a.getAttribute('href') || '').trim();
      if (/^https?:\/\//i.test(href)) {
        a.setAttribute('target', '_blank');
        a.setAttribute('rel', 'noopener noreferrer');
      } else {
        a.removeAttribute('href');
      }
    });

    container.querySelectorAll('img').forEach(function (img) {
      var src = (img.getAttribute('src') || '').trim();
      if (!/^https?:\/\//i.test(src)) {
        img.removeAttribute('src');
      }
    });

    return container.innerHTML;
  }

  function renderMarkdown(text) {
    return sanitizeHtml(marked.parse(text.replace(/</g, '&lt;'), { gfm: true, breaks: true }));
  }

  function addUserMessage(text) {
    var div = document.createElement('div');
    div.className = 'msg msg-user';
    div.textContent = text;
    thread.appendChild(div);
    thread.scrollTop = thread.scrollHeight;
    return div;
  }

  function addAssistantMessage(text, citations) {
    var div = document.createElement('div');
    div.className = 'msg msg-assistant';
    var body = document.createElement('div');
    body.className = 'msg-body';
    body.innerHTML = renderMarkdown(text);
    div.appendChild(body);
    if (citations && citations.length) {
      div.appendChild(buildCitationStrip(citations));
    }
    thread.appendChild(div);
    thread.scrollTop = thread.scrollHeight;
    return { el: div, body: body };
  }

  function addSystemMessage(text, isError) {
    var div = document.createElement('div');
    div.className = 'msg msg-system' + (isError ? ' msg-error' : '');
    div.textContent = text;
    thread.appendChild(div);
    thread.scrollTop = thread.scrollHeight;
  }

  function buildCitationStrip(citations) {
    var strip = document.createElement('div');
    strip.className = 'citations';
    citations.forEach(function (c) {
      var chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'citation-chip';
      chip.textContent = c.label;
      chip.onclick = function () {
        if (c.source === 'lab') {
          fetch(API + '/lab-link?notebook=' + encodeURIComponent(c.notebook))
            .then(function (r) { return r.json(); })
            .then(function (d) { if (d.url) window.open(d.url, '_blank'); });
        } else {
          window.deckViewer.open(c.deck_id, c.h, c.v);
        }
      };
      strip.appendChild(chip);
    });
    return strip;
  }

  // --- composer + streaming ------------------------------------------------

  function setStreaming(on) {
    streaming = on;
    input.disabled = on;
    sendBtn.disabled = on;
  }

  function autoGrow() {
    input.style.height = 'auto';
    input.style.height = input.scrollHeight + 'px';
  }
  input.addEventListener('input', autoGrow);

  function send() {
    var question = input.value.trim();
    if (!question || streaming) return;

    addUserMessage(question);
    input.value = '';
    input.style.height = '';
    setStreaming(true);

    requestSeq += 1;
    var seq = requestSeq;
    var controller = new AbortController();

    var liveBuffer = '';
    var liveHandle = null;
    var lastRender = 0;
    var pendingTimer = null;

    function isCurrent() {
      return activeRequest !== null && activeRequest.seq === seq;
    }

    function cancel() {
      controller.abort();
      if (pendingTimer) {
        clearTimeout(pendingTimer);
        pendingTimer = null;
      }
    }

    activeRequest = { seq: seq, cancel: cancel };

    function finish() {
      if (isCurrent()) activeRequest = null;
      setStreaming(false);
    }

    function ensureBubble() {
      if (!liveHandle) liveHandle = addAssistantMessage('', []);
      return liveHandle;
    }

    function renderNow() {
      var h = ensureBubble();
      h.body.innerHTML = renderMarkdown(liveBuffer);
      thread.scrollTop = thread.scrollHeight;
      lastRender = Date.now();
    }

    function scheduleRender() {
      var elapsed = Date.now() - lastRender;
      if (elapsed >= RENDER_INTERVAL_MS) {
        renderNow();
      } else if (!pendingTimer) {
        pendingTimer = setTimeout(function () {
          pendingTimer = null;
          renderNow();
        }, RENDER_INTERVAL_MS - elapsed);
      }
    }

    function flush() {
      if (pendingTimer) {
        clearTimeout(pendingTimer);
        pendingTimer = null;
      }
      renderNow();
    }

    function handleFrame(frame) {
      if (!isCurrent()) return;
      if (!frame.trim()) return;
      var event = 'message', data = null;
      frame.split('\n').forEach(function (line) {
        if (line.indexOf('event:') === 0) event = line.slice(6).trim();
        else if (line.indexOf('data:') === 0) data = line.slice(5).trim();
      });
      if (data === null) return;
      var payload;
      try { payload = JSON.parse(data); } catch (e) { return; }

      if (event === 'meta') {
        conversationId = payload.conversation_id;
        refreshConversations();
      } else if (event === 'token') {
        liveBuffer += payload.text;
        scheduleRender();
      } else if (event === 'citations') {
        var h = ensureBubble();
        var existing = h.el.querySelector('.citations');
        if (existing) existing.remove();
        h.el.appendChild(buildCitationStrip(payload));
        thread.scrollTop = thread.scrollHeight;
      } else if (event === 'done') {
        flush();
        finish();
      } else if (event === 'error') {
        addSystemMessage(payload.message, true);
        finish();
      }
    }

    var cur = window.deckViewer.current() || {};
    fetch(API + '/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: controller.signal,
      body: JSON.stringify({
        conversation_id: conversationId,
        deck: cur.deck || null,
        slide: cur.slide || null,
        message: question
      })
    }).then(function (res) {
      if (!isCurrent()) return;
      if (!res.ok) {
        return res.json().catch(function () {
          return { message: 'The tutor is unavailable right now.' };
        }).then(function (err) {
          if (!isCurrent()) return;
          addSystemMessage(err.message || 'The tutor is unavailable right now.', true);
          finish();
        });
      }
      var reader = res.body.getReader();
      var decoder = new TextDecoder();
      var buf = '';

      function pump() {
        return reader.read().then(function (result) {
          if (!isCurrent()) return;
          if (result.done) {
            flush();
            finish();
            return;
          }
          buf += decoder.decode(result.value, { stream: true });
          var frames = buf.split('\n\n');
          buf = frames.pop();
          frames.forEach(handleFrame);
          return pump();
        });
      }

      return pump();
    }).catch(function (err) {
      if (err && err.name === 'AbortError') return;
      if (!isCurrent()) return;
      addSystemMessage('Lost the connection to the tutor.', true);
      finish();
    });
  }

  sendBtn.onclick = send;
  input.addEventListener('keydown', function (ev) {
    if (ev.key === 'Enter' && !ev.shiftKey) {
      ev.preventDefault();
      send();
    }
  });

  // --- startup ---------------------------------------------------------

  window.deckViewer.onChange(updateContext);

  fetch(API + '/me').catch(function () {});
  updateContext();
  refreshConversations();
})();
