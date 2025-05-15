document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('crud-container');
    if (!container) return;

    const baseUrl   = container.dataset.baseUrl;
    const listUrl   = container.dataset.listUrl;
    
    // Crear
    container.querySelector('.btn-create').addEventListener('click', () => {
      const form = container.querySelector('.form-create');
      const data = {};
      form.querySelectorAll('[name]').forEach(inp => {
        data[inp.name] = inp.value.trim();
      });
      // validación básica
      if (!data.nombre) return alert('El nombre no puede ir vacío');
      
      fetch(baseUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      .then(r => {
        if (!r.ok) throw new Error('Error al crear');
        return r.json();
      })
      .then(() => window.location.href = listUrl)
      .catch(e => alert(e.message));
    });
  
    // Delegación para editar, guardar, cancelar y borrar
    container.addEventListener('click', e => {
      const btn = e.target;
      // Toggle edición
      if (btn.matches('.btn-edit')) {
        const itemId = btn.dataset.id;
        container
          .querySelector(`.form-edit[data-id="${itemId}"]`)
          .classList.toggle('d-none');
      }
  
      // Guardar cambios
      if (btn.matches('.btn-save')) {
        const itemId = btn.dataset.id;
        const form   = container.querySelector(`.form-edit[data-id="${itemId}"]`);
        const data   = {};
        form.querySelectorAll('[name]').forEach(inp => {
          data[inp.name] = inp.value.trim();
        });
        fetch(`${baseUrl}/${itemId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        })
        .then(r => r.json())
        .then(() => window.location.href = listUrl)
        .catch(console.error);
      }
  
      // Cancelar edición
      if (btn.matches('.btn-cancel')) {
        const itemId = btn.dataset.id;
        container
          .querySelector(`.form-edit[data-id="${itemId}"]`)
          .classList.add('d-none');
      }
  
      // Eliminar
      if (btn.matches('.btn-delete')) {
        const itemId = btn.dataset.id;
        if (!confirm('¿Seguro que deseas eliminar?')) return;
        fetch(`${baseUrl}/${itemId}`, { method: 'DELETE' })
        .then(r => {
          if (!r.ok) throw new Error('Falló eliminación');
          window.location.href = listUrl;
        })
        .catch(e => alert(e.message));
      }
    });
  });
  