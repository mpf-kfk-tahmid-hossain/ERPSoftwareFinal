function getCookie(name){const v=`; ${document.cookie}`.split(`; ${name}=`);return v.length===2?v.pop().split(';').shift():'';}
const csrftoken = getCookie('csrftoken');

async function fetchChildren(parentId){
  let url = CATEGORY_CHILDREN_URL;
  if(parentId){ url += `?parent_id=${parentId}`; }
  const resp = await fetch(url, {headers:{'X-Requested-With':'XMLHttpRequest'}});
  if(resp.ok) return await resp.json();
  return [];
}

function createNode(cat){
  const li = document.createElement('li');
  li.className = 'mb-1';
  li.dataset.id = cat.id;

  const div = document.createElement('div');
  div.className = 'd-flex align-items-center';

  const expand = document.createElement('button');
  expand.className = 'btn btn-sm btn-light me-1 expand-btn';
  expand.textContent = '+';
  if(!cat.has_children) expand.classList.add('d-none');
  expand.addEventListener('click', async () => {
    const container = li.querySelector('ul');
    if(container.childElementCount){
      container.innerHTML='';
      expand.classList.remove('btn-secondary');
      return;
    }
    const children = await fetchChildren(cat.id);
    children.forEach(c => container.appendChild(createNode(c)));
    if(children.length===0) expand.classList.add('d-none');
    else expand.classList.add('btn-secondary');
  });
  div.appendChild(expand);

  const name = document.createElement('span');
  name.className = 'cat-name flex-grow-1';
  name.textContent = cat.name;
  div.appendChild(name);
  if(cat.is_discontinued){
    name.insertAdjacentHTML('afterend',' <span class="badge bg-danger">\u274C Discontinued</span>');
  }

  const rename = document.createElement('button');
  rename.className = 'btn btn-sm btn-link rename-btn';
  rename.textContent = 'Rename';
  rename.addEventListener('click', async () => {
    const newName = prompt('New name', cat.name);
    if(!newName) return;
    const resp = await fetch(`/inventory/categories/${cat.id}/rename/`,{method:'POST',headers:{'X-CSRFToken':csrftoken},body:new URLSearchParams({name:newName})});
    if(resp.ok){
      name.textContent = newName;
      cat.name = newName;
    }
  });
  div.appendChild(rename);

  const disc = document.createElement('button');
  disc.className = 'btn btn-sm btn-link text-danger discontinue-btn';
  disc.textContent = 'Discontinue';
  disc.addEventListener('click', async () => {
    if(!confirm('Discontinue category and its children?')) return;
    const resp = await fetch(`/inventory/categories/${cat.id}/discontinue/`,{method:'POST',headers:{'X-CSRFToken':csrftoken}});
    if(resp.ok){ li.querySelectorAll('button').forEach(b=>b.remove()); name.insertAdjacentHTML('afterend',' <span class="badge bg-danger">\u274C Discontinued</span>'); }
  });
  div.appendChild(disc);
  if(cat.is_discontinued){
    rename.classList.add('d-none');
    disc.classList.add('d-none');
  }

  li.appendChild(div);
  const ul = document.createElement('ul');
  ul.className = 'ms-4 list-unstyled';
  li.appendChild(ul);

  return li;
}

async function loadRoot(){
  const root = document.getElementById('category-root');
  const cats = await fetchChildren('');
  cats.forEach(c => root.appendChild(createNode(c)));
}

async function loadDepth(parentId, depth, container){
  if(depth===0) return;
  const children = await fetchChildren(parentId);
  children.forEach(async c => {
    const node = createNode(c);
    container.appendChild(node);
    if(depth>1 && c.has_children){
      const childUl = node.querySelector('ul');
      await loadDepth(c.id, depth-1, childUl);
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  loadRoot();
  document.getElementById('depth-btn').addEventListener('click', async () => {
    const d = prompt('Load depth');
    const depth = parseInt(d);
    if(!depth || depth<1) return;
    const root = document.getElementById('category-root');
    root.innerHTML='';
    await loadDepth('', depth, root);
  });
});
