function searchUrl(type){
  if(type==='Product') return '/inventory/products/search/';
  if(type==='Service') return '/purchasing/services/search/';
  if(type==='Office Supply') return '/purchasing/office-supplies/search/';
  if(type==='Asset/Capex') return '/purchasing/assets/search/';
  if(type==='IT/Software') return '/purchasing/it-software/search/';
  return '';
}

function initSelect(select, url){
  $(select).select2({
    theme:'bootstrap-5',
    ajax:{
      url:url,
      dataType:'json',
      delay:250,
      data:params=>({q:params.term}),
      processResults:data=>data
    },
    width:'100%',
    placeholder:'Search...'
  }).on('select2:select', function(e){
    const d=e.params.data;const row=$(this).closest('.row');
    row.find('input[name="line_desc"]').val(d.description); row.find('input[name="line_unit"]').val(d.unit);
  });
}

function addLine(){
  const container=document.getElementById('line-items');
  const type=document.getElementById('id_type').value;
  const div=document.createElement('div');
  div.className='border p-2 mb-2';
  div.innerHTML=`<div class="row g-2 align-items-end">
    <div class="col-md-3"><label class="form-label">Name</label>
      <select class="form-select item-select" name="line_name" required></select>
    </div>
    <div class="col-md-3"><label class="form-label">Description</label>
      <input type="text" class="form-control" name="line_desc">
    </div>
    <div class="col-md-2"><label class="form-label">Qty</label>
      <input type="number" step="any" class="form-control" name="line_qty">
    </div>
    <div class="col-md-2"><label class="form-label">Unit</label>
      <input type="text" class="form-control" name="line_unit">
    </div>
    <div class="col-md-2"><label class="form-label">Justification</label>
      <input type="text" class="form-control" name="line_just">
    </div>
    <div class="col-md-1 text-end"><button type="button" class="btn btn-danger btn-sm remove-line">&times;</button></div>
  </div>`;
  container.appendChild(div);
  div.querySelector('.remove-line').onclick=()=>{div.remove();updateSummary();};
  div.querySelector('input[name="line_qty"]').addEventListener('input', updateSummary);
  const select=div.querySelector('.item-select');
  initSelect(select, searchUrl(type));
  updateSummary();
}
function collect(){
  const items=[];
  document.querySelectorAll('#line-items > div').forEach(div=>{
    const sel=div.querySelector('.item-select');
    const n=$(sel).find(':selected').text();
    const d=div.querySelector('input[name="line_desc"]').value;
    const j=div.querySelector('input[name="line_just"]').value;
    const q=div.querySelector('input[name="line_qty"]').value;
    const u=div.querySelector('input[name="line_unit"]').value;
    items.push({name:n,description:d,justification:j,quantity:q,unit:u});
  });
  document.getElementById('items_json').value=JSON.stringify(items);
}

function updateSummary(){
  const lines=document.querySelectorAll('#line-items > div');
  let total=0;
  lines.forEach(div=>{
    const q=parseFloat(div.querySelector('input[name="line_qty"]').value)||0;
    total+=q;
  });
  document.getElementById('summary-text').textContent=`Total lines: ${lines.length}, Total qty: ${total}`;
}

document.getElementById('add-line').addEventListener('click', addLine);
document.querySelector('form').addEventListener('submit', collect);
addLine();
updateSummary();
