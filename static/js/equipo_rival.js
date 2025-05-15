// equipo_rival.js
document.addEventListener('DOMContentLoaded', function() {
  const container = document.getElementById('crud-integrantes-rivales-container');
  const baseUrl = container.getAttribute('data-base-url');
  const anchor = '#integrantes';
  // Crear
  container.querySelector('.btn-create').addEventListener('click', async () => {
    const data = Object.fromEntries(new FormData(container.querySelector('.form-create')).entries());
    try { const res = await fetch(baseUrl, { method: 'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) }); if(!res.ok) throw ''; window.location.hash=anchor; window.location.reload(); } catch(e){alert('Error al crear');}
  });
  // Delegación
  container.addEventListener('click', e=>{
    const id = e.target.dataset.id;
    if(e.target.classList.contains('btn-edit')) toggle(id,true);
    if(e.target.classList.contains('btn-cancel')) toggle(id,false);
    if(e.target.classList.contains('btn-save')) save(id);
    if(e.target.classList.contains('btn-delete')) del(id);
  });
  function toggle(id,show){const item=container.querySelector(`[data-id="${id}"]`), form=item.querySelector('.form-edit'), visibles=[...item.children].filter(c=>!c.classList.contains('form-edit')); if(show){form.classList.remove('d-none'); visibles.forEach(c=>c.classList.add('d-none'));} else{form.classList.add('d-none'); visibles.forEach(c=>c.classList.remove('d-none'));}}
  async function save(id){const item=container.querySelector(`.form-edit[data-id="${id}"]`), data={}; item.querySelectorAll('input').forEach(i=>data[i.name]=i.value); try{const r=await fetch(`${baseUrl}/${id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}); if(!r.ok)throw'';window.location.hash=anchor;window.location.reload();}catch(e){alert('Error al actualizar');}}
  async function del(id){if(!confirm('¿Eliminar?'))return; try{const r=await fetch(`${baseUrl}/${id}`,{method:'DELETE'}); if(!r.ok)throw'';window.location.hash=anchor;window.location.reload();}catch(e){alert('Error al eliminar');}}
});

