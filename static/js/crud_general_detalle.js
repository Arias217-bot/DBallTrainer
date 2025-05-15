document.addEventListener("DOMContentLoaded", () => {
    // Inicializar CRUD para integrantes, mensajes y torneos
    const crudContainers = document.querySelectorAll("[id^=crud-][id$=-container]");
    crudContainers.forEach(initCrud);
  
    function initCrud(container) {
      // Base URL (sin slash final) para todos los endpoints CRUD
      const rawUrl = container.dataset.baseUrl;
      const baseEndpoint = rawUrl.replace(/\/$/, '');
      const listUrl = container.dataset.listUrl;
  
      // Obtener el ID real de la entidad (id_usuario_equipo para integrantes)
      function getEntityId(btn) {
        // Primero intentamos con data-entity-id (recomendado)
        if (btn.dataset.entityId) {
          return btn.dataset.entityId;
        }
        // Para usuario_equipo (integrantes), extraemos id_usuario_equipo de un span oculto
        if (baseEndpoint.endsWith('/usuario_equipo')) {
          const item = btn.closest('.list-group-item');
          const idSpan = item.querySelector('.item-value.id_usuario_equipo');
          if (idSpan) return idSpan.textContent;
        }
        // Fallback al data-id (por defecto documento o id)
        return btn.dataset.id;
      }
  
      // Mapear campos personalizados a la estructura esperada por el backend
      function mapPayload(data) {
        const payload = { ...data };
        // Para integrantes: renombrar rol -> id_rol, posicion -> id_posicion
        if ('rol' in payload) { payload.id_rol = payload.rol; delete payload.rol; }
        if ('posicion' in payload) { payload.id_posicion = payload.posicion; delete payload.posicion; }
        return payload;
      }
  
      // CREATE
      const createBtn = container.querySelector(".btn-create");
      if (createBtn) {
        createBtn.addEventListener("click", () => {
          const form = container.querySelector(".form-create");
          const data = {};
          new FormData(form).forEach((value, key) => { data[key] = value; });
          const payload = mapPayload(data);
  
          fetch(baseEndpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          })
          .then(res => {
            if (!res.ok) throw new Error("Error al crear");
            return res.json();
          })
          .then(() => {
            // Recargar la página en la pestaña correspondiente
            location.reload();
          })
          .catch(err => alert(err.message));
        });
      }
  
      // DELETE
      container.querySelectorAll(".btn-delete").forEach(btn => {
        btn.addEventListener("click", () => {
          const id = getEntityId(btn);
          if (!confirm("¿Seguro quieres eliminar este elemento?")) return;
  
          fetch(`${baseEndpoint}/${id}`, { method: "DELETE" })
            .then(res => {
              if (!res.ok) throw new Error("Error al eliminar");
              // Remover elemento del DOM
              const item = btn.closest('.list-group-item');
              if (item) item.remove();
            })
            .catch(err => alert(err.message));
        });
      });
  
      // EDIT: mostrar formulario
      container.querySelectorAll(".btn-edit").forEach(btn => {
        btn.addEventListener("click", () => {
          const formContainer = container.querySelector(`.form-edit[data-id='${btn.dataset.id}']`);
          if (formContainer) formContainer.classList.remove("d-none");
        });
      });
  
      // EDIT: cancelar
      container.querySelectorAll(".btn-cancel").forEach(btn => {
        btn.addEventListener("click", () => {
          const formContainer = container.querySelector(`.form-edit[data-id='${btn.dataset.id}']`);
          if (formContainer) formContainer.classList.add("d-none");
        });
      });
  
      // EDIT: guardar cambios
      container.querySelectorAll(".btn-save").forEach(btn => {
        btn.addEventListener("click", () => {
          const id = getEntityId(btn);
          const formContainer = container.querySelector(`.form-edit[data-id='${btn.dataset.id}']`);
          if (!formContainer) return;
  
          const data = {};
          formContainer.querySelectorAll('input[name], select[name], textarea[name]').forEach(el => {
            data[el.name] = el.value;
          });
          const payload = mapPayload(data);
  
          fetch(`${baseEndpoint}/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          })
          .then(res => {
            if (!res.ok) throw new Error("Error al actualizar");
            return res.json();
          })
          .then(updated => {
            // Actualizar valores en el DOM
            const item = btn.closest('.list-group-item');
            if (item) {
              Object.entries(updated).forEach(([key, value]) => {
                const span = item.querySelector(`.item-value.${key}`);
                if (span) span.textContent = value;
              });
              formContainer.classList.add("d-none");
            }
          })
          .catch(err => alert(err.message));
        });
      });
    }
  });
  
  /*** Importante ***/
  // Para que el script reconozca correctamente el ID de 'usuario_equipo', añade en tu plantilla detalle_equipo.html:
  // en cada <button> de eliminar/editar/guardar/cancelar para integrantes:
  //   data-entity-id="{{ integrante.id_usuario_equipo }}"
  // o un <span class="d-none item-value id_usuario_equipo">{{ integrante.id_usuario_equipo }}</span>
  // Esto permite usar el ID real (id_usuario_equipo) en lugar del 'documento'.