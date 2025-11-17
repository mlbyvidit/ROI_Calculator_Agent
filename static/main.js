const msgs = [];

function append(role, content) {
  msgs.push({ role, content });
  const div = document.createElement('div');
  div.className = 'msg ' + (role === 'user' ? 'user' : 'assistant');
  div.textContent = content;
  document.getElementById('messages').appendChild(div);
}

async function send() {
  const input = document.getElementById('input');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  append('user', text);
  const res = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages: msgs }),
  });
  const data = await res.json();
  append('assistant', data.reply);
  const dl = document.getElementById('download');
  if (data.pdf_base64 && data.filename) {
    dl.style.display = 'inline-block';
    dl.onclick = () => {
      const b = atob(data.pdf_base64);
      const len = b.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) bytes[i] = b.charCodeAt(i);
      const blob = new Blob([bytes], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = data.filename;
      a.click();
      URL.revokeObjectURL(url);
    };
  }
}

document.getElementById('send').addEventListener('click', send);
document.getElementById('input').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') send();
});