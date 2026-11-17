const timerEl = document.getElementById('timer');
const btn = document.getElementById('finish-btn');
const start = Date.now();

function fmt(sec) {
  const m = String(Math.floor(sec / 60)).padStart(2, '0');
  const s = String(Math.floor(sec % 60)).padStart(2, '0');
  return `${m}:${s}`;
}

const interval = setInterval(() => {
  timerEl.textContent = fmt((Date.now() - start) / 1000);
}, 500);

btn.addEventListener('click', async () => {
  clearInterval(interval);
  btn.disabled = true;
  try {
    const resp = await fetch(btn.dataset.finishUrl);
    const data = await resp.json();
    document.getElementById('final-time').textContent = fmt(data.seconds);
  } catch (e) {
    document.getElementById('final-time').textContent = timerEl.textContent;
  }
  document.getElementById('text-block').classList.add('d-none');
  document.getElementById('done-block').classList.remove('d-none');
  btn.classList.add('d-none');
});