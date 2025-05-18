// Mapa de zonas de voleibol (nuestro equipo abajo, rival arriba)
const zonas = {
    'z1': { x: 16.66, y: 87.5, nombre: 'Z1', clase: 'zona-1', centerX: 16.66, centerY: 87.5 },
    'z2': { x: 50, y: 87.5, nombre: 'Z2', clase: 'zona-2', centerX: 50, centerY: 87.5 },
    'z3': { x: 83.33, y: 87.5, nombre: 'Z3', clase: 'zona-3', centerX: 83.33, centerY: 87.5 },
    'z4': { x: 16.66, y: 62.5, nombre: 'Z4', clase: 'zona-4', centerX: 16.66, centerY: 62.5 },
    'z5': { x: 50, y: 62.5, nombre: 'Z5', clase: 'zona-5', centerX: 50, centerY: 62.5 },
    'z6': { x: 83.33, y: 62.5, nombre: 'Z6', clase: 'zona-6', centerX: 83.33, centerY: 62.5 },
    'z7': { x: 16.66, y: 12.5, nombre: 'Z7', clase: 'zona-7', centerX: 16.66, centerY: 12.5 },
    'z8': { x: 50, y: 12.5, nombre: 'Z8', clase: 'zona-8', centerX: 50, centerY: 12.5 },
    'z9': { x: 83.33, y: 12.5, nombre: 'Z9', clase: 'zona-9', centerX: 83.33, centerY: 12.5 },
    'z10': { x: 16.66, y: 37.5, nombre: 'Z10', clase: 'zona-10', centerX: 16.66, centerY: 37.5 },
    'z11': { x: 50, y: 37.5, nombre: 'Z11', clase: 'zona-11', centerX: 50, centerY: 37.5 },
    'z12': { x: 83.33, y: 37.5, nombre: 'Z12', clase: 'zona-12', centerX: 83.33, centerY: 37.5 }
};

// Variables de estado
let jugadaActual = null;
let pasoActual = 0;
let intervaloReproduccion = null;
let pasosProcesados = [];
let reproduccionAutomaticaActiva = false;
let indiceJugadaActual = 0;
let intervaloReproduccionAutomatica = null;
let todasLasJugadas = [];

// Inicialización del campo
function inicializarCancha() {
    const cancha = document.getElementById('cancha');
    cancha.innerHTML = '<div class="red-line"></div>';
    
    Object.entries(zonas).forEach(([key, zona]) => {
        const divZona = document.createElement('div');
        divZona.className = `zona ${zona.clase}`;
        divZona.textContent = zona.nombre;
        cancha.appendChild(divZona);
    });
}

// Función mejorada para dibujar líneas
function dibujarLinea(inicio, fin, clase = '') {
    const linea = document.createElement('div');
    linea.className = `jugada-linea ${clase}`;
    
    // Obtener coordenadas en porcentaje
    const startX = inicio.centerX;
    const startY = inicio.centerY;
    const endX = fin.centerX;
    const endY = fin.centerY;
    
    // Calcular diferencias
    const dx = endX - startX;
    const dy = endY - startY;
    
    // Calcular en píxeles
    const canchaContainer = document.querySelector('.cancha-container');
    const containerWidth = canchaContainer.offsetWidth;
    const containerHeight = containerWidth * 0.45; // Relación 45% definida en CSS
    
    const startXPx = (startX / 100) * containerWidth;
    const startYPx = (startY / 100) * containerHeight;
    const endXPx = (endX / 100) * containerWidth;
    const endYPx = (endY / 100) * containerHeight;
    
    // Calcular longitud y ángulo
    const lengthPx = Math.sqrt(Math.pow(endXPx - startXPx, 2) + Math.pow(endYPx - startYPx, 2));
    const angle = Math.atan2(endYPx - startYPx, endXPx - startXPx) * 180 / Math.PI;
    
    // Aplicar estilos
    Object.assign(linea.style, {
        width: `${lengthPx}px`,
        left: `${startX}%`,
        top: `${startY}%`,
        transform: `rotate(${angle}deg)`,
        transformOrigin: '0 0',
        position: 'absolute',
        height: '2px',
        backgroundColor: 'rgba(255, 255, 255, 0.7)'
    });
    
    document.getElementById('cancha').appendChild(linea);
    return linea;
}

// Mostrar marcador de acción
function mostrarAccion(posicion, tipoAccion, evaluacion) {
    const marker = document.createElement('div');
    marker.className = 'accion-marker';
    marker.style.left = `${posicion.centerX}%`;
    marker.style.top = `${posicion.centerY}%`;
    
    const iconos = {
        saque: '⚽', recibo: '✋', pase: '⇨', remate: '⚡',
        bloqueo: '🛑', defensa: '✋', contraataque: '↷', libre: '○', toque: '•'
    };
    
    const clases = {
        '++': 'excelente', '+': 'buena', '=': 'normal',
        '-': 'mala', '--': 'error'
    };
    
    marker.textContent = iconos[tipoAccion] || tipoAccion.substring(0,1);
    marker.classList.add(clases[evaluacion]);
    marker.title = `${tipoAccion} (${evaluacion})`;
    
    document.getElementById('cancha').appendChild(marker);
}

// Cargar y mostrar jugada
function cargarJugada(secuencia, datosProcesados) {
    const cancha = document.getElementById('cancha');
    cancha.innerHTML = '<div class="red-line"></div>';
    inicializarCancha();
    
    jugadaActual = null;
    pasoActual = 0;
    pasosProcesados = [];
    clearInterval(intervaloReproduccion);
    
    document.getElementById('currentStep').textContent = '0/0';
    document.getElementById('jugadaProgress').style.width = '0%';
    
    if (!secuencia) {
        document.getElementById('jugadaInfo').innerHTML = '<p class="text-muted small">Selecciona una jugada del historial para visualizarla</p>';
        return;
    }
    
    if (datosProcesados?.pasos) {
        // Asegurar que cada paso tenga su posición
        pasosProcesados = datosProcesados.pasos.map(paso => ({
            ...paso,
            posicion: zonas[paso.zona] || { centerX: 50, centerY: 50 } // Valor por defecto si no encuentra la zona
        }));
    } else {
        // Procesamiento para secuencias sin datos procesados
        pasosProcesados = secuencia.split(',')
            .map(paso => paso.match(/j(\d+)(z\d+)(\w+)([\+\-\=]{1,2})/))
            .filter(match => match)
            .map(match => ({
                tipo: 'accion_completa',
                jugador: `j${match[1]}`,
                zona: match[2],
                tipoAccion: match[3],
                evaluacion: match[4],
                posicion: zonas[match[2]] || { centerX: 50, centerY: 50 } // Valor por defecto
            }));
    }
    
    jugadaActual = secuencia;
    document.getElementById('currentStep').textContent = `0/${pasosProcesados.length}`;
    document.getElementById('jugadaInfo').innerHTML = `
        <p class="mb-1"><strong>Jugada:</strong> ${secuencia}</p>
        <p class="small text-muted">${pasosProcesados.length} pasos registrados</p>
    `;
    mostrarPaso(0);
}

// Mostrar paso específico
function mostrarPaso(indice) {
    if (!jugadaActual || indice < 0 || indice >= pasosProcesados.length) return;
    
    // Limpiar elementos anteriores
    document.querySelectorAll('.jugador-marker, .jugada-linea, .letrero-paso').forEach(el => el.remove());
    
    let prevPos = null;
    
    for (let i = 0; i <= indice; i++) {
        const paso = pasosProcesados[i];
        
        if (paso.tipo === 'accion_completa') {
            // Marcador del jugador
            const marker = document.createElement('div');
            marker.className = `jugador-marker ${paso.zona.startsWith('z7') ? 'rival-marker' : ''}`;
            Object.assign(marker.style, {
                left: `${paso.posicion.centerX}%`,
                top: `${paso.posicion.centerY}%`,
                transform: 'translate(-50%, -50%)',
                width: '60px',
                height: '60px',
                fontSize: '1.2rem'
            });
            marker.textContent = paso.jugador;
            document.getElementById('cancha').appendChild(marker);
            
            // Línea de trayectoria
            if (prevPos) {
                dibujarLinea(prevPos, paso.posicion);
            }
            
            // Letrero solo para el paso actual
            if (i === indice) {
                const iconos = {
                    saque: '⚽', recibo: '✋', pase: '➡', remate: '⚡',
                    bloqueo: '🛑', defensa: '✋', contraataque: '↷', libre: '○', toque: '•'
                };
                
                const evaluaciones = {
                    '++': 'Excelente', '+': 'Buena', '=': 'Normal',
                    '-': 'Mala', '--': 'Error'
                };
                
                const letrero = document.createElement('div');
                letrero.className = 'letrero-paso';
                letrero.style.left = `${paso.posicion.centerX}%`;
                letrero.style.top = `${paso.posicion.centerY - 2}%`;

                const simbolo = document.createElement('div');
                simbolo.className = 'letrero-simbolo';
                simbolo.textContent = iconos[paso.tipoAccion] || paso.tipoAccion.charAt(0);

                const texto = document.createElement('div');
                texto.className = 'letrero-texto';

                const accion = document.createElement('div');
                accion.textContent = paso.tipoAccion;

                const evaluacion = document.createElement('div');
                const small = document.createElement('small');
                small.textContent = evaluaciones[paso.evaluacion];
                evaluacion.appendChild(small);

                texto.appendChild(accion);
                texto.appendChild(evaluacion);

                letrero.appendChild(simbolo);
                letrero.appendChild(texto);

                document.getElementById('cancha').appendChild(letrero);
            }
            
            prevPos = paso.posicion;
        }
    }
    
    // Actualizar controles
    pasoActual = indice;
    document.getElementById('currentStep').textContent = `${pasoActual + 1}/${pasosProcesados.length}`;
    document.getElementById('jugadaProgress').style.width = `${(pasoActual + 1) / pasosProcesados.length * 100}%`;
}

// Controles de reproducción
function reproducirJugada() {
    if (!jugadaActual || pasosProcesados.length === 0) return;
    pausarJugada();
    
    if (pasoActual >= pasosProcesados.length - 1) {
        if (reproduccionAutomaticaActiva) {
            indiceJugadaActual++;
            reproducirSiguienteJugadaAutomatica();
            return;
        }
        pasoActual = -1;
    }
    
    intervaloReproduccion = setInterval(() => {
        pasoActual++;
        mostrarPaso(pasoActual);
        
        if (pasoActual >= pasosProcesados.length - 1) {
            if (reproduccionAutomaticaActiva) {
                clearInterval(intervaloReproduccion);
                indiceJugadaActual++;
                reproducirSiguienteJugadaAutomatica();
            } else {
                pausarJugada();
            }
        }
    }, 1000);
}

function pausarJugada() {
    clearInterval(intervaloReproduccion);
    intervaloReproduccion = null;
    if (reproduccionAutomaticaActiva) {
        clearTimeout(intervaloReproduccionAutomatica);
    }
}

// Reproducción automática
function prepararReproduccionAutomatica() {
    todasLasJugadas = Array.from(document.querySelectorAll('.jugada-item'));
    indiceJugadaActual = 0;
    reproduccionAutomaticaActiva = true;
    if (todasLasJugadas.length > 0) {
        reproducirSiguienteJugadaAutomatica();
    }
}

function reproducirSiguienteJugadaAutomatica() {
    if (indiceJugadaActual >= todasLasJugadas.length) {
        finalizarReproduccionAutomatica();
        return;
    }
    
    const jugada = todasLasJugadas[indiceJugadaActual];
    todasLasJugadas.forEach(j => j.classList.remove('table-primary'));
    jugada.classList.add('table-primary');
    jugada.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    cargarJugada(jugada.dataset.secuencia, jugada.dataset.procesada ? JSON.parse(jugada.dataset.procesada) : null);
    setTimeout(reproducirJugada, 500);
}

function finalizarReproduccionAutomatica() {
    clearTimeout(intervaloReproduccionAutomatica);
    reproduccionAutomaticaActiva = false;
    todasLasJugadas.forEach(j => j.classList.remove('table-primary'));
    document.getElementById('reproducirTodasBtn').innerHTML = '<i class="bi bi-collection-play"></i> Reproducir Todas';
}

function toggleReproduccionAutomatica() {
    const boton = document.getElementById('reproducirTodasBtn');
    if (reproduccionAutomaticaActiva) {
        finalizarReproduccionAutomatica();
        boton.innerHTML = '<i class="bi bi-collection-play"></i> Reproducir Todas';
    } else {
        prepararReproduccionAutomatica();
        boton.innerHTML = '<i class="bi bi-stop-fill"></i> Detener Reproducción';
    }
}

// Eventos del DOM
document.addEventListener('DOMContentLoaded', () => {
    inicializarCancha();

    // Formulario
    document.querySelector('.agregar-paso').addEventListener('click', function() {
        const jugador = document.querySelector('.jugador-input').value;
        const zona = document.querySelector('.zona-input').value;
        const tipoAccion = document.querySelector('.tipo-accion-input').value;
        const evaluacion = document.querySelector('.accion-input').value;
        
        if (!jugador) {
            alert('Por favor ingresa un número de jugador');
            return;
        }
        
        const secuencia = document.getElementById('secuencia_jugada');
        const current = secuencia.value ? secuencia.value.split(',') : [];
        current.push(`j${jugador}${zona}${tipoAccion}${evaluacion}`);
        secuencia.value = current.join(',');
    });

    document.getElementById('jugadaForm').addEventListener('submit', function(e) {
        e.preventDefault();
        fetch('/partido/procesar-jugada/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(Object.fromEntries(new FormData(this)))
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                location.reload();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al guardar la jugada');
        });
    });

    // Historial
    document.querySelectorAll('.jugada-item').forEach(item => {
        item.addEventListener('click', function(e) {
            if (e.target.classList.contains('borrar-jugada')) return;
            cargarJugada(this.dataset.secuencia, this.dataset.procesada ? JSON.parse(this.dataset.procesada) : null);
            bootstrap.Tab.getInstance(document.querySelector('#visualizacion-tab')).show();
        });
        
        item.querySelector('.borrar-jugada').addEventListener('click', function(e) {
            e.stopPropagation();
            if (confirm('¿Estás seguro de que deseas borrar esta jugada?')) {
                fetch(`/jugadas/${this.closest('.jugada-item').dataset.id}`, { method: 'DELETE' })
                .then(response => {
                    if (response.ok) location.reload(); else alert('Error al borrar la jugada');
                })
                .catch(err => { console.error('Error:', err); alert('Error al borrar la jugada'); });
            }
        });
    });

    // Filtro
    document.getElementById('filtroJugadas').addEventListener('input', function() {
        const filtro = this.value.toLowerCase();
        document.querySelectorAll('.jugada-item').forEach(item => {
            item.style.display = item.textContent.toLowerCase().includes(filtro) ? '' : 'none';
        });
    });

    // Controles
    document.getElementById('reproducirJugada').addEventListener('click', reproducirJugada);
    document.getElementById('pausarJugada').addEventListener('click', pausarJugada);
    document.getElementById('reiniciarJugada').addEventListener('click', () => { pasoActual = -1; mostrarPaso(0); });
    document.getElementById('avanzarJugada').addEventListener('click', () => { if (pasoActual < pasosProcesados.length - 1) mostrarPaso(pasoActual + 1); });
    document.getElementById('retrocederJugada').addEventListener('click', () => { if (pasoActual > 0) mostrarPaso(pasoActual - 1); });
    document.getElementById('reproducirTodasBtn').addEventListener('click', toggleReproduccionAutomatica);

    const nombrePartido = decodeURIComponent(window.location.pathname.split('/').pop()).replace(/-/g, ' ');

    // Estadísticas
    document.getElementById('estadisticas-tab').addEventListener('click', function() {
        if (typeof nombrePartido === 'undefined' || !nombrePartido) {
            console.error('Nombre del partido no definido');
            return;
        }
        
        fetch(`/partido/${encodeURIComponent(nombrePartido)}/estadisticas`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    // Mostrar mensaje amigable
                    document.getElementById('estadisticas').innerHTML = `
                        <div class="alert alert-info">
                            ${data.error}
                        </div>`;
                } else {
                    mostrarEstadisticas(data);
                }
            })
            .catch(error => {
                console.error('Error al cargar estadísticas:', error);
                document.getElementById('estadisticas').innerHTML = `
                    <div class="alert alert-warning">
                        Error al cargar estadísticas: ${error.message}
                    </div>`;
            });
    });
});

// Mostrar estadísticas
function mostrarEstadisticas(data) {
    // Rendimiento por jugador
    const cuerpoTabla = document.getElementById('cuerpo-rendimiento');
    cuerpoTabla.innerHTML = '';
    for (const [jugador, stats] of Object.entries(data.rendimiento_jugadores || {})) {
        const fila = document.createElement('tr');
        fila.innerHTML = `
            <td>Jugador ${jugador}</td>
            <td>${stats.porcentaje_excelente?.toFixed(1) || 0}%</td>
            <td>${stats.porcentaje_efectivo?.toFixed(1) || 0}%</td>
            <td>${stats.porcentaje_error?.toFixed(1) || 0}%</td>
            <td>${stats.total_acciones}</td>
        `;
        cuerpoTabla.appendChild(fila);
    }

    // Gráficos
    crearGrafico('grafico-zonas', 'bar', Object.keys(data.distribucion_zonas || {}), Object.values(data.distribucion_zonas || {}), 'Distribución de Zonas de Ataque');
    crearGraficoStacked('grafico-tipos-accion', data.efectividad_por_tipo || {}, 'Efectividad por Tipo de Acción');
    crearGrafico('grafico-equipos', 'pie', ['Nuestro equipo', 'Equipo rival'], [data.comparativa_equipos?.nuestro || 0, data.comparativa_equipos?.rival || 0], 'Comparativa de Equipos');
}

function crearGrafico(id, tipo, labels, data, titulo) {
    const ctx = document.getElementById(id).getContext('2d');
    if (window[`grafico${id}`]) window[`grafico${id}`].destroy();
    
    window[`grafico${id}`] = new Chart(ctx, {
        type: tipo,
        data: {
            labels: tipo === 'pie' ? labels : labels.map(l => `Zona ${l}`),
            datasets: [{
                data: data,
                backgroundColor: tipo === 'pie' ? 
                    ['rgba(54, 162, 235, 0.7)', 'rgba(255, 99, 132, 0.7)'] : 
                    ['rgba(54, 162, 235, 0.7)'],
                borderColor: tipo === 'pie' ? 
                    ['rgba(54, 162, 235, 1)', 'rgba(255, 99, 132, 1)'] : 
                    ['rgba(54, 162, 235, 1)'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: tipo === 'pie' ? 'bottom' : 'top' },
                title: { display: !!titulo, text: titulo }
            },
            scales: tipo !== 'pie' ? { y: { beginAtZero: true } } : undefined
        }
    });
}

function crearGraficoStacked(id, datos, titulo) {
    const ctx = document.getElementById(id).getContext('2d');
    if (window[`grafico${id}`]) window[`grafico${id}`].destroy();
    
    const tipos = Object.keys(datos);
    const exitosos = tipos.map(t => datos[t].exitosos || 0);
    const normales = tipos.map(t => (datos[t].total - datos[t].exitosos - datos[t].fallados) || 0);
    const fallados = tipos.map(t => datos[t].fallados || 0);
    
    window[`grafico${id}`] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: tipos,
            datasets: [
                { label: 'Éxitosos', data: exitosos, backgroundColor: 'rgba(75, 192, 192, 0.7)' },
                { label: 'Normales', data: normales, backgroundColor: 'rgba(255, 206, 86, 0.7)' },
                { label: 'Fallados', data: fallados, backgroundColor: 'rgba(255, 99, 132, 0.7)' }
            ]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true, stacked: true }, x: { stacked: true } },
            plugins: { title: { display: true, text: titulo } }
        }
    });
}