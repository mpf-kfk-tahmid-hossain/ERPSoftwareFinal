let lineIndex=0;
function addLine(){
  const container=document.getElementById('line-items');
  const div=document.createElement('div');
  div.className='border p-2 mb-2';
  div.innerHTML=`<div class="row g-2 align-items-end">
    <div class="col-md-3"><label class="form-label">Type</label>
      <select class="form-select" name="line_type">
        <option value="Product">Product</option>
        <option value="Office Supply">Office Supply</option>
        <option value="Service">Service</option>
        <option value="Other">Other</option>
      </select>
    </div>
    <div class="col-md-4"><label class="form-label">Description</label>
      <input type="text" class="form-control" name="line_desc">
    </div>
    <div class="col-md-2"><label class="form-label">Qty</label>
      <input type="number" step="any" class="form-control" name="line_qty">
    </div>
    <div class="col-md-2"><label class="form-label">Unit</label>
      <input type="text" class="form-control" name="line_unit">
    </div>
    <div class="col-md-1 text-end"><button type="button" class="btn btn-danger btn-sm remove-line">&times;</button></div>
  </div>`;
  container.appendChild(div);
  div.querySelector('.remove-line').onclick=()=>{div.remove();updateSummary();};
  div.querySelector('input[name="line_qty"]').addEventListener('input', updateSummary);
  updateSummary();
}
function collect(){
  const items=[];
  document.querySelectorAll('#line-items > div').forEach(div=>{
    const t=div.querySelector('select[name="line_type"]').value;
    const d=div.querySelector('input[name="line_desc"]').value;
    const q=div.querySelector('input[name="line_qty"]').value;
    const u=div.querySelector('input[name="line_unit"]').value;
    items.push({type:t,description:d,quantity:q,unit:u});
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
