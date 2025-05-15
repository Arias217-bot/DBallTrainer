// Verificar token y cargar el perfil
async function loadProfile() {
    const token = localStorage.getItem('token');

    if (!token) {
        alert('No tienes autorización. Inicia sesión.');
        window.location.href = '/login';
        return;
    }

    try {
        const response = await fetch('/profile', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            alert('Sesión expirada o no válida. Vuelve a iniciar sesión.');
            logout();
            return;
        }

        const usuario = await response.json();

        // Actualizar los campos con los datos del usuario
        document.getElementById('documento').textContent = usuario.documento || 'N/A';
        document.getElementById('nombre').textContent = usuario.nombre || 'N/A';
        document.getElementById('email').textContent = usuario.email || 'N/A';
        document.getElementById('fecha_nacimiento').textContent = usuario.fecha_nacimiento || 'N/A';
        document.getElementById('sexo').textContent = usuario.sexo || 'N/A';
        document.getElementById('telefono').textContent = usuario.telefono || 'N/A';
        document.getElementById('direccion').textContent = usuario.direccion || 'N/A';
        document.getElementById('experiencia').textContent = usuario.experiencia || 'N/A';
    } catch (error) {
        console.error('Error al cargar el perfil:', error);
        alert('Error al obtener los datos del perfil.');
        logout();
    }
}

// Función para cerrar sesión
function logout() {
    localStorage.removeItem('token');  // Eliminar el token
    window.location.href = '/login';  // Redirigir al login
}

// Cargar el perfil al cargar la página
document.addEventListener('DOMContentLoaded', loadProfile);
