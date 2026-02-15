async function postMessage(content) {
  const res = await fetch('/api/messages', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content })
  });
  return res.json();
}

async function loadMessages() {
  const res = await fetch('/api/messages?limit=200');
  const messages = await res.json();
  const list = document.getElementById('list');
  list.innerHTML = '';
  if (!messages.length) {
    list.textContent = 'No messages yet.';
    return;
  }
  for (const m of messages) {
    const el = document.createElement('div');
    el.className = 'message';
    const date = new Date(m.created_at);
    el.innerHTML = `<div class="meta">${date.toLocaleString()}</div><div class="body">${escapeHtml(m.content)}</div>`;
    list.appendChild(el);
  }
}

function escapeHtml(s) {
  return s.replace(/[&<>\"]+/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

document.getElementById('msgForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const ta = document.getElementById('content');
  const val = ta.value.trim();
  if (!val) return;
  try {
    await postMessage(val);
    ta.value = '';
    loadMessages();
  } catch (err) {
    alert('Failed to send message');
  }
});

document.getElementById('refresh').addEventListener('click', loadMessages);
window.addEventListener('load', loadMessages);
