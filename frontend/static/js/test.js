const form = document.getElementById('test-form');
const bar = document.getElementById('progress');
const total = form.querySelectorAll('.question-card').length;

form.addEventListener('change', () => {
  const answered = new Set(
    [...form.querySelectorAll('input[type=radio]:checked')].map(i => i.name)
  ).size;
  bar.style.width = (total ? answered / total * 100 : 0) + '%';
});