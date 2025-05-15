// static/js/videos.js

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('crud-container');
    if (!container) return;
  
    // URLs
    const uploadUrl = container.dataset.baseUrl;            // /videos/upload
    const listUrl   = container.dataset.listUrl;            // /videos/ver
    // API base para edición/eliminación (quita '/upload')
    const apiBase   = uploadUrl.replace(/\/upload$/, '');  // /videos
  
    const uploadForm = container.querySelector('.form-create');
  
    // Subida de video con FormData
    if (uploadForm) {
      uploadForm.addEventListener('submit', e => {
        e.preventDefault();
        const formData = new FormData(uploadForm);
  
        fetch(uploadUrl, {
          method: 'POST',
          body: formData
        })
        .then(res => {
          if (!res.ok) throw new Error('Error al subir el video');
          return res.json();
        })
        .then(() => window.location.href = listUrl)
        .catch(err => alert(err.message));
      });
    }
  
    // Delegación para editar, guardar, cancelar y eliminar
    container.addEventListener('click', e => {
      const btn = e.target;
      const itemId = btn.dataset.id;
      if (!itemId) return;
  
      // Mostrar/Ocultar formulario de edición
      if (btn.matches('.btn-edit')) {
        const formEdit = container.querySelector(`.form-edit[data-id="${itemId}"]`);
        if (formEdit) formEdit.classList.toggle('d-none');
      }
  
      // Guardar cambios (PUT)
      if (btn.matches('.btn-save')) {
        const formEdit = container.querySelector(`.form-edit[data-id="${itemId}"]`);
        const data = {};
        formEdit.querySelectorAll('[name]').forEach(input => {
          data[input.name] = input.value.trim();
        });
        fetch(`${apiBase}/${itemId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        })
        .then(res => {
          if (!res.ok) throw new Error('Error al guardar');
          return res.json();
        })
        .then(() => window.location.href = listUrl)
        .catch(err => alert(err.message));
      }
  
      // Cancelar edición
      if (btn.matches('.btn-cancel')) {
        const formEdit = container.querySelector(`.form-edit[data-id="${itemId}"]`);
        if (formEdit) formEdit.classList.add('d-none');
      }
  
      // Eliminar video (DELETE)
      if (btn.matches('.btn-delete')) {
        if (!confirm('¿Seguro que deseas eliminar este video?')) return;
        fetch(`${apiBase}/${itemId}`, {
          method: 'DELETE'
        })
        .then(res => {
          if (!res.ok) throw new Error('Error al eliminar');
          window.location.href = listUrl;
        })
        .catch(err => alert(err.message));
      }
    });
  });
  