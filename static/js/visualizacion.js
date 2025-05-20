// Mapa de zonas de voleibol (nuestro equipo abajo, rival arriba)
const zonas = {
    'z5': { x: 16.66, y: 87.5, nombre: 'Z5', clase: 'zona-5', centerX: 16.66, centerY: 87.5 },
    'z6': { x: 50, y: 87.5, nombre: 'Z6', clase: 'zona-6', centerX: 50, centerY: 87.5 },
    'z1': { x: 83.33, y: 87.5, nombre: 'Z1', clase: 'zona-1', centerX: 83.33, centerY: 87.5 },
    'z2': { x: 16.66, y: 62.5, nombre: 'Z2', clase: 'zona-2', centerX: 16.66, centerY: 62.5 },
    'z3': { x: 50, y: 62.5, nombre: 'Z3', clase: 'zona-3', centerX: 50, centerY: 62.5 },
    'z4': { x: 83.33, y: 62.5, nombre: 'Z4', clase: 'zona-4', centerX: 83.33, centerY: 62.5 },
    'zr1': { x: 16.66, y: 12.5, nombre: 'ZR1', clase: 'zona-rival-1', centerX: 16.66, centerY: 12.5 },
    'zr6': { x: 50, y: 12.5, nombre: 'ZR6', clase: 'zona-rival-6', centerX: 50, centerY: 12.5 },
    'zr5': { x: 83.33, y: 12.5, nombre: 'ZR5', clase: 'zona-rival-5', centerX: 83.33, centerY: 12.5 },
    'zr2': { x: 16.66, y: 37.5, nombre: 'ZR2', clase: 'zona-rival-2', centerX: 16.66, centerY: 37.5 },
    'zr3': { x: 50, y: 37.5, nombre: 'ZR3', clase: 'zona-rival-3', centerX: 50, centerY: 37.5 },
    'zr4': { x: 83.33, y: 37.5, nombre: 'ZR4', clase: 'zona-rival-4', centerX: 83.33, centerY: 37.5 }
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
    
    // Calcular en píxeles
    const canchaContainer = document.querySelector('.cancha-container');
    const containerWidth = canchaContainer.offsetWidth;
    const containerHeight = containerWidth * 0.45;
    
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
        saque: '🏐', recibo: '✋', pase: '⇨', remate: '⚡',
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
        pasosProcesados = datosProcesados.pasos.map(paso => ({
            ...paso,
            posicion: zonas[paso.zona] || { centerX: 50, centerY: 50 }
        }));
    } else {
        pasosProcesados = secuencia.split(',')
            .map(paso => paso.match(/j(\d+)(z\d+)(\w+)([\+\-\=]{1,2})/))
            .filter(match => match)
            .map(match => ({
                tipo: 'accion_completa',
                jugador: `j${match[1]}`,
                zona: match[2],
                tipoAccion: match[3],
                evaluacion: match[4],
                posicion: zonas[match[2]] || { centerX: 50, centerY: 50 }
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
    
    document.querySelectorAll('.jugador-marker, .jugada-linea, .letrero-paso').forEach(el => el.remove());
    
    let prevPos = null;
    
    for (let i = 0; i <= indice; i++) {
        const paso = pasosProcesados[i];
        
        if (paso.tipo === 'accion_completa') {
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
            
            if (prevPos) {
                dibujarLinea(prevPos, paso.posicion);
            }
            
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

// ==================== ESTADÍSTICAS MEJORADAS ====================

// Función principal para mostrar estadísticas
function mostrarEstadisticas(data) {
    if (!data) {
        console.error('No se recibieron datos de estadísticas');
        return;
    }

    // Actualizar resumen general
    actualizarResumenGeneral(data.resumen_general || {});

    // Gráfico de distribución de zonas
    crearGraficoZonas(data.distribucion_zonas || {});

    // Gráfico de efectividad por tipo de acción
    crearGraficoEfectividad(data.efectividad_por_tipo || {});

    // Gráfico comparativo de equipos
    crearGraficoEquipos(data.comparativa_equipos || {});

    // Tabla de resumen por tipo de acción
    llenarTablaAcciones(data.efectividad_por_tipo || {});

    // Tabla de rendimiento por jugador
    llenarTablaJugadores(data.rendimiento_jugadores || {});
}

function actualizarResumenGeneral(resumen) {
    document.getElementById('total-acciones').textContent = resumen.acciones_totales || '--';
    document.getElementById('porcentaje-exitos').textContent = resumen.porcentaje_efectivo?.toFixed(1) || '--';
    document.getElementById('porcentaje-normales').textContent = resumen.porcentaje_normal?.toFixed(1) || '--';
    document.getElementById('porcentaje-errores').textContent = resumen.porcentaje_error?.toFixed(1) || '--';
    
    document.getElementById('excelentes-count').textContent = resumen.excelentes || '--';
    document.getElementById('buenas-count').textContent = resumen.buenas || '--';
    document.getElementById('normales-count').textContent = resumen.normales || '--';
    document.getElementById('errores-count').textContent = resumen.errores || '--';
    document.getElementById('malas-count').textContent = resumen.malas || '--';
}

function crearGraficoZonas(datosZonas) {
    const zonasOrdenadas = Object.entries(datosZonas)
        .sort((a, b) => b[1] - a[1]);
    
    const labels = zonasOrdenadas.map(([zona]) => `Zona ${zona.substring(1)}`);
    const data = zonasOrdenadas.map(([_, count]) => count);
    
    // Crear tabla de zonas
    const tablaZonas = document.getElementById('tabla-zonas');
    tablaZonas.innerHTML = `
        <div class="d-flex flex-wrap gap-2 justify-content-center">
            ${zonasOrdenadas.map(([zona, count]) => `
                <span class="badge bg-primary">
                    ${zona}: ${count} acción${count !== 1 ? 'es' : ''}
                </span>
            `).join('')}
        </div>
    `;
    
    // Crear gráfico
    crearGrafico('grafico-zonas', 'bar', labels, data, 'Distribución por Zonas');
}

function crearGraficoEfectividad(datosEfectividad) {
    const tipos = Object.keys(datosEfectividad);
    const exitosos = tipos.map(t => datosEfectividad[t].exitosos || 0);
    const normales = tipos.map(t => (datosEfectividad[t].normales || 0));
    const fallados = tipos.map(t => (datosEfectividad[t].fallados || 0));
    
    const ctx = document.getElementById('grafico-tipos-accion').getContext('2d');
    if (window.graficoTiposAccion) window.graficoTiposAccion.destroy();
    
    window.graficoTiposAccion = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: tipos.map(t => t.charAt(0).toUpperCase() + t.slice(1)),
            datasets: [
                { 
                    label: 'Excelentes', 
                    data: exitosos, 
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                },
                { 
                    label: 'Normales', 
                    data: normales, 
                    backgroundColor: 'rgba(255, 206, 86, 0.7)',
                    borderColor: 'rgba(255, 206, 86, 1)',
                    borderWidth: 1
                },
                { 
                    label: 'Fallados', 
                    data: fallados, 
                    backgroundColor: 'rgba(255, 99, 132, 0.7)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: { 
                y: { beginAtZero: true, stacked: false }, 
                x: { stacked: false } 
            },
            plugins: { 
                title: { display: true, text: 'Efectividad por Tipo de Acción' },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const tipo = tipos[context.dataIndex];
                            const datos = datosEfectividad[tipo];
                            const total = datos.total || 1;
                            const porcentaje = (context.dataset.data[context.dataIndex] / total * 100).toFixed(1);
                            return `Efectividad: ${porcentaje}%`;
                        }
                    }
                }
            }
        }
    });
}

function crearGraficoEquipos(datosEquipos) {
    const ctx = document.getElementById('grafico-equipos').getContext('2d');
    
    // Crear tabla comparativa
    const detalleEquipos = document.getElementById('detalle-equipos');
    detalleEquipos.innerHTML = `
        <div class="row text-center">
            <div class="col-md-6">
                <h6>Nuestro Equipo</h6>
                <p>Efectividad: ${datosEquipos.nuestro?.porcentaje_efectivo?.toFixed(1) || 0}%</p>
                <p>Excelentes: ${datosEquipos.nuestro?.excelentes || 0}</p>
            </div>
            <div class="col-md-6">
                <h6>Equipo Rival</h6>
                <p>Efectividad: ${datosEquipos.rival?.porcentaje_efectivo?.toFixed(1) || 0}%</p>
                <p>Errores: ${datosEquipos.rival?.errores || 0}</p>
            </div>
        </div>
    `;
    
    if (window.graficoEquipos) window.graficoEquipos.destroy();
    
    window.graficoEquipos = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Nuestro equipo', 'Equipo rival'],
            datasets: [{
                data: [
                    datosEquipos.nuestro?.total || 0, 
                    datosEquipos.rival?.total || 0
                ],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 99, 132, 0.7)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' },
                title: { display: true, text: 'Acciones por Equipo' },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const equipo = context.label === 'Nuestro equipo' ? 'nuestro' : 'rival';
                            const datos = datosEquipos[equipo] || {};
                            return `Efectividad: ${datos.porcentaje_efectivo?.toFixed(1) || 0}%`;
                        }
                    }
                }
            }
        }
    });
}

function llenarTablaAcciones(datosAcciones) {
    const tabla = document.getElementById('tabla-resumen-acciones');
    tabla.innerHTML = Object.entries(datosAcciones)
        .map(([tipo, datos]) => {
            const total = datos.total || 1;
            const efectividad = ((datos.exitosos || 0) / total * 100).toFixed(1);
            
            return `
                <tr>
                    <td class="text-start">${tipo.charAt(0).toUpperCase() + tipo.slice(1)}</td>
                    <td>${datos.exitosos || 0}</td>
                    <td>${(datos.buenas || 0)}</td>
                    <td>${datos.normales || 0}</td>
                    <td>${(datos.malas || 0)}</td>
                    <td>${datos.fallados || 0}</td>
                    <td>${total}</td>
                    <td>
                        <span class="badge ${efectividad >= 70 ? 'bg-success' : 
                            efectividad >= 40 ? 'bg-warning' : 'bg-danger'}">
                            ${efectividad}%
                        </span>
                    </td>
                </tr>
            `;
        })
        .join('');
}

function llenarTablaJugadores(datosJugadores) {
    const tabla = document.getElementById('cuerpo-rendimiento');
    
    const jugadoresOrdenados = Object.entries(datosJugadores)
        .sort(([numA], [numB]) => parseInt(numA) - parseInt(numB));
    
    tabla.innerHTML = jugadoresOrdenados
        .map(([numero, datos]) => {
            const total = datos.total_acciones || 1;
            const efectividad = datos.porcentaje_efectivo?.toFixed(1) || 
                (((datos.excelentes || 0) + (datos.buenas || 0)) / total * 100).toFixed(1);
            
            return `
                <tr>
                    <td class="text-start">Jugador ${numero}</td>
                    <td>${datos.excelentes || 0}</td>
                    <td>${datos.buenas || 0}</td>
                    <td>${datos.normales || 0}</td>
                    <td>${datos.malas || 0}</td>
                    <td>${datos.errores || 0}</td>
                    <td>${total}</td>
                    <td>
                        <span class="badge ${efectividad >= 70 ? 'bg-success' : 
                            efectividad >= 40 ? 'bg-warning' : 'bg-danger'}">
                            ${efectividad}%
                        </span>
                    </td>
                </tr>
            `;
        })
        .join('');
}

// Función genérica para crear gráficos
function crearGrafico(id, tipo, labels, data, titulo) {
    const ctx = document.getElementById(id).getContext('2d');
    if (window[`grafico${id}`]) window[`grafico${id}`].destroy();
    
    window[`grafico${id}`] = new Chart(ctx, {
        type: tipo,
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: tipo === 'pie' || tipo === 'doughnut' ? 
                    ['rgba(54, 162, 235, 0.7)', 'rgba(255, 99, 132, 0.7)'] : 
                    ['rgba(54, 162, 235, 0.7)'],
                borderColor: tipo === 'pie' || tipo === 'doughnut' ? 
                    ['rgba(54, 162, 235, 1)', 'rgba(255, 99, 132, 1)'] : 
                    ['rgba(54, 162, 235, 1)'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: tipo === 'pie' || tipo === 'doughnut' ? 'bottom' : 'top' },
                title: { display: !!titulo, text: titulo }
            },
            scales: tipo !== 'pie' && tipo !== 'doughnut' ? { y: { beginAtZero: true } } : undefined
        }
    });
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
        fetch('/partido/procesar-jugada', {
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

    // Estadísticas
    document.getElementById('estadisticas-tab').addEventListener('click', function() {
        // Obtener el nombre del partido de manera segura
        const nombrePartido = document.getElementById('partido-data')?.dataset.nombre || 
                            "{{ partido.nombre_partido|default('', true)|escapejs }}";
        
        if (!nombrePartido || nombrePartido.includes('{{')) {
            console.error('Nombre del partido no disponible');
            document.getElementById('estadisticas').innerHTML = `
                <div class="alert alert-danger">
                    Error: No se pudo obtener el nombre del partido
                </div>`;
            return;
        }

        fetch(`/partido/${encodeURIComponent(nombrePartido)}/estadisticas`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
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