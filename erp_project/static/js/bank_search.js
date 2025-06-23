(document.addEventListener('DOMContentLoaded', function () {
  const input = document.getElementById('id_bank_name');
  const list = document.getElementById('bank-options');
  if (!input || !list) return;
  input.addEventListener('input', function () {
    const q = input.value.trim();
    if (q.length < 2) return;
    fetch(`/purchasing/banks/search/?q=${encodeURIComponent(q)}`)
      .then(r => r.json())
      .then(data => {
        list.innerHTML = '';
        data.forEach(b => {
          const opt = document.createElement('option');
          opt.value = b.name;
          list.appendChild(opt);
        });
      });
  });
}));
