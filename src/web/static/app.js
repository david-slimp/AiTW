(() => {
  const transcript = document.getElementById('transcript');
  const cmd = document.getElementById('cmd');
  const send = document.getElementById('send');
  const statusRoom = document.getElementById('status-room');

  const exitsEl = document.getElementById('exits');
  const hereEl = document.getElementById('here');
  const groundEl = document.getElementById('ground');
  const invEl = document.getElementById('inv');

  function addLine(text, cls) {
    const p = document.createElement('div');
    p.className = 'line' + (cls ? (' ' + cls) : '');
    p.textContent = text;
    transcript.appendChild(p);
    transcript.scrollTop = transcript.scrollHeight;
  }

  function renderList(ul, items) {
    ul.innerHTML = '';
    (items || []).forEach((t) => {
      const li = document.createElement('li');
      li.textContent = t;
      ul.appendChild(li);
    });
  }

  function renderRoom(room) {
    if (!room) return;
    statusRoom.textContent = `${room.name} (${room.id})`;

    const exitKeys = room.exits ? Object.keys(room.exits) : [];
    if (exitKeys.length === 0) {
      renderList(exitsEl, ['(none)']);
    } else {
      renderList(exitsEl, exitKeys.map(k => `${k} -> ${room.exits[k]}`));
    }

    renderList(hereEl, room.players || []);
    renderList(groundEl, room.items || []);
  }

  function renderInventory(inv) {
    const items = (inv && inv.items) ? inv.items : [];
    renderList(invEl, items.length ? items : ['(empty)']);
  }

  function sendCmd(text) {
    const t = (text || '').trim();
    if (!t) return;
    ws.send(JSON.stringify({ type: 'cmd', text: t }));
    cmd.value = '';
    cmd.focus();
  }

  const proto = (location.protocol === 'https:') ? 'wss' : 'ws';
  const ws = new WebSocket(`${proto}://${location.host}/ws`);

  ws.addEventListener('open', () => {
    addLine('(Connected)', 'muted');
    cmd.focus();
  });

  ws.addEventListener('message', (ev) => {
    let msg;
    try { msg = JSON.parse(ev.data); } catch (e) { return; }

    if (msg.type === 'log') {
      addLine(msg.text);
      return;
    }

    if (msg.type === 'init') {
      renderRoom(msg.room);
      renderInventory(msg.inventory);
      return;
    }

    if (msg.type === 'room_state') {
      renderRoom(msg.room);
      return;
    }

    if (msg.type === 'inv_state') {
      renderInventory(msg.inventory);
      return;
    }
  });

  ws.addEventListener('close', () => {
    addLine('(Disconnected)', 'muted');
    statusRoom.textContent = 'Disconnected';
  });

  send.addEventListener('click', () => sendCmd(cmd.value));
  cmd.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendCmd(cmd.value);
  });

  document.querySelectorAll('button.q').forEach((b) => {
    b.addEventListener('click', () => sendCmd(b.dataset.cmd || ''));
  });
})();
