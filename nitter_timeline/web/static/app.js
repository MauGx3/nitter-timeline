async function loadTimeline() {
  const feedsValue = document.getElementById('feeds').value.trim();
  const params = new URLSearchParams();
  if (feedsValue) {
    feedsValue.split(',').map(v => v.trim()).filter(Boolean).forEach(f => params.append('feeds', f));
  }
  const res = await fetch('/api/timeline?' + params.toString(), {credentials: 'same-origin'});
  const data = await res.json();
  const el = document.getElementById('timeline');
  el.innerHTML = '';
  for (const item of data.items) {
    const div = document.createElement('article');
    div.className = 'tweet';
    div.innerHTML = `
      <div class="meta">${item.author || ''} ${item.published ? new Date(item.published).toLocaleString() : ''}</div>
      <div class="content">${item.content_html || item.summary || ''}</div>
    `;
    el.appendChild(div);
  }
}

function initTimeline() {
  document.getElementById('feed-form').addEventListener('submit', (e) => { e.preventDefault(); loadTimeline(); });
  loadTimeline();
}

document.addEventListener('DOMContentLoaded', initTimeline);
