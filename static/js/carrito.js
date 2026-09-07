/**
 * Carrito de Compras Reactivo para TechStore
 * - Almacenamiento persistente en localStorage
 * - Descuento dinámico del stock en la página
 * - Modal lateral derecho (Bootstrap 5 Offcanvas)
 * - Formato monetario chileno (CLP)
 */

const STORAGE_KEY = 'techstore_carrito_v1';

function obtenerCarrito() {
    try {
        const guardado = localStorage.getItem(STORAGE_KEY);
        return guardado ? JSON.parse(guardado) : [];
    } catch (e) {
        console.error('Error al leer carrito:', e);
        return [];
    }
}

function guardarCarrito(carrito) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(carrito));
    actualizarUI();
}

function formatoCLP(monto) {
    return '$' + Math.round(monto).toLocaleString('es-CL');
}

function obtenerCantidadEnCarrito(id) {
    const carrito = obtenerCarrito();
    const item = carrito.find(p => p.id === parseInt(id));
    return item ? item.cantidad : 0;
}

function agregarAlCarrito(id, nombre, precio, stockTotal, imagen) {
    id = parseInt(id);
    precio = parseInt(precio);
    stockTotal = parseInt(stockTotal);

    let carrito = obtenerCarrito();
    let item = carrito.find(p => p.id === id);

    const cantidadActual = item ? item.cantidad : 0;

    if (cantidadActual >= stockTotal) {
        alert(`¡No puedes agregar más unidades! Solo quedan ${stockTotal} unidades en stock.`);
        return;
    }

    if (item) {
        item.cantidad += 1;
    } else {
        carrito.push({
            id: id,
            nombre: nombre,
            precio: precio,
            stockTotal: stockTotal,
            imagen: imagen,
            cantidad: 1
        });
    }

    guardarCarrito(carrito);

    // Abrir automáticamente el modal lateral derecho
    const offcanvasEl = document.getElementById('offcanvasCarrito');
    if (offcanvasEl) {
        const bsOffcanvas = bootstrap.Offcanvas.getOrCreateInstance(offcanvasEl);
        bsOffcanvas.show();
    }
}

function cambiarCantidad(id, delta) {
    id = parseInt(id);
    let carrito = obtenerCarrito();
    let item = carrito.find(p => p.id === id);

    if (!item) return;

    const nuevaCantidad = item.cantidad + delta;

    if (nuevaCantidad > item.stockTotal) {
        alert(`No hay suficiente stock. El máximo disponible es ${item.stockTotal} unidades.`);
        return;
    }

    if (nuevaCantidad <= 0) {
        carrito = carrito.filter(p => p.id !== id);
    } else {
        item.cantidad = nuevaCantidad;
    }

    guardarCarrito(carrito);
}

function eliminarDelCarrito(id) {
    id = parseInt(id);
    let carrito = obtenerCarrito();
    carrito = carrito.filter(p => p.id !== id);
    guardarCarrito(carrito);
}

function vaciarCarrito() {
    if (confirm('¿Estás seguro de que deseas vaciar todos los productos del carrito?')) {
        guardarCarrito([]);
    }
}

function finalizarCompra() {
    const carrito = obtenerCarrito();
    if (carrito.length === 0) {
        alert('Tu carrito está vacío.');
        return;
    }

    const total = carrito.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);
    alert(`¡Compra procesada con éxito!\n\nTotal pagado: ${formatoCLP(total)}\nGracias por tu compra en TechStore.`);
    guardarCarrito([]);
    
    // Cerrar el modal lateral
    const offcanvasEl = document.getElementById('offcanvasCarrito');
    if (offcanvasEl) {
        const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvasEl);
        if (bsOffcanvas) bsOffcanvas.hide();
    }
}

function actualizarUI() {
    const carrito = obtenerCarrito();

    // 1. Actualizar contador del Navbar
    const badge = document.getElementById('badgeContadorCarrito');
    const totalArticulos = carrito.reduce((acc, item) => acc + item.cantidad, 0);
    if (badge) {
        badge.textContent = totalArticulos;
        badge.style.display = totalArticulos > 0 ? 'inline-block' : 'none';
    }

    // 2. Renderizar items en el panel lateral (Offcanvas)
    const contenedorItems = document.getElementById('carritoItems');
    const contenedorFooter = document.getElementById('carritoFooter');

    if (contenedorItems) {
        if (carrito.length === 0) {
            contenedorItems.innerHTML = `
                <div class="text-center py-5 text-muted">
                    <div class="display-1 text-secondary opacity-25 mb-3">
                        <i class="bi bi-cart-x"></i>
                    </div>
                    <h5 class="fw-bold">Tu carrito está vacío</h5>
                    <p class="small">Explora nuestro catálogo y agrega productos a tu compra.</p>
                </div>
            `;
            if (contenedorFooter) contenedorFooter.style.display = 'none';
        } else {
            let html = '<div class="list-group list-group-flush">';
            let granTotal = 0;

            carrito.forEach(item => {
                const subtotal = item.precio * item.cantidad;
                granTotal += subtotal;
                const stockRestante = item.stockTotal - item.cantidad;

                html += `
                    <div class="list-group-item px-0 py-3 border-bottom">
                        <div class="d-flex gap-3">
                            <img src="${item.imagen}" alt="${item.nombre}" class="rounded-3 border" style="width: 65px; height: 65px; object-fit: cover;">
                            <div class="flex-grow-1">
                                <h6 class="fw-bold mb-1 text-truncate" style="max-width: 200px;" title="${item.nombre}">
                                    ${item.nombre}
                                </h6>
                                <div class="text-primary fw-bold mb-1">${formatoCLP(item.precio)}</div>
                                <div class="text-muted small mb-2">
                                    <i class="bi bi-box-seam me-1"></i>Stock restante: <strong class="${stockRestante === 0 ? 'text-danger' : 'text-success'}">${stockRestante}</strong>
                                </div>
                                
                                <div class="d-flex justify-content-between align-items-center">
                                    <div class="btn-group btn-group-sm border rounded-pill overflow-hidden" role="group">
                                        <button type="button" class="btn btn-light px-2" onclick="cambiarCantidad(${item.id}, -1)">
                                            <i class="bi bi-dash"></i>
                                        </button>
                                        <span class="btn btn-light px-3 fw-bold disabled border-start border-end text-dark">${item.cantidad}</span>
                                        <button type="button" class="btn btn-light px-2" onclick="cambiarCantidad(${item.id}, 1)" ${item.cantidad >= item.stockTotal ? 'disabled' : ''}>
                                            <i class="bi bi-plus"></i>
                                        </button>
                                    </div>

                                    <div class="d-flex align-items-center gap-2">
                                        <span class="fw-bold text-dark">${formatoCLP(subtotal)}</span>
                                        <button class="btn btn-sm text-danger border-0 p-1" onclick="eliminarDelCarrito(${item.id})" title="Eliminar">
                                            <i class="bi bi-trash fs-6"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });

            html += '</div>';
            contenedorItems.innerHTML = html;

            if (contenedorFooter) {
                contenedorFooter.style.display = 'block';
                contenedorFooter.innerHTML = `
                    <div class="d-flex justify-content-between align-items-baseline mb-3">
                        <span class="fs-6 text-muted">Total a Pagar:</span>
                        <span class="fs-4 fw-bold text-primary">${formatoCLP(granTotal)}</span>
                    </div>
                    <div class="d-grid gap-2">
                        <button class="btn btn-success btn-lg rounded-pill fw-semibold shadow-sm" onclick="finalizarCompra()">
                            <i class="bi bi-credit-card me-1"></i> Finalizar Compra
                        </button>
                        <button class="btn btn-outline-secondary btn-sm rounded-pill" onclick="vaciarCarrito()">
                            <i class="bi bi-trash me-1"></i> Vaciar Carrito
                        </button>
                    </div>
                `;
            }
        }
    }

    // 3. Descontar dinámicamente el stock visible en la página actual
    document.querySelectorAll('[data-stock-producto-id]').forEach(el => {
        const id = parseInt(el.getAttribute('data-stock-producto-id'));
        const stockTotal = parseInt(el.getAttribute('data-stock-total'));
        const cantidadEnCarro = obtenerCantidadEnCarrito(id);
        const restante = Math.max(0, stockTotal - cantidadEnCarro);

        // Actualizamos el texto y color del indicador de stock
        if (restante > 5) {
            el.innerHTML = `<span class="badge bg-success-subtle text-success border border-success-subtle px-3 py-2 rounded-pill"><i class="bi bi-check-circle-fill me-1"></i> En Stock (${restante} un.)</span>`;
        } else if (restante > 0) {
            el.innerHTML = `<span class="badge bg-warning-subtle text-warning-emphasis border border-warning-subtle px-3 py-2 rounded-pill"><i class="bi bi-exclamation-triangle-fill me-1"></i> ¡Últimas ${restante} un.!</span>`;
        } else {
            el.innerHTML = `<span class="badge bg-danger-subtle text-danger border border-danger-subtle px-3 py-2 rounded-pill"><i class="bi bi-x-circle-fill me-1"></i> Agotado</span>`;
        }
    });

    // 4. Habilitar o deshabilitar botones de "Agregar al Carrito" según el stock restante
    document.querySelectorAll('[data-btn-producto-id]').forEach(btn => {
        const id = parseInt(btn.getAttribute('data-btn-producto-id'));
        const stockTotal = parseInt(btn.getAttribute('data-stock-total'));
        const cantidadEnCarro = obtenerCantidadEnCarrito(id);
        const restante = stockTotal - cantidadEnCarro;

        if (restante <= 0) {
            btn.disabled = true;
            btn.classList.add('disabled');
            btn.innerHTML = `<i class="bi bi-slash-circle me-1"></i> Agotado`;
        } else {
            btn.disabled = false;
            btn.classList.remove('disabled');
            btn.innerHTML = `<i class="bi bi-cart-plus me-1"></i> Agregar al Carrito`;
        }
    });
}

// Inicializar al cargar el DOM
document.addEventListener('DOMContentLoaded', () => {
    actualizarUI();

    // Capturar clicks en botones con clase "btn-agregar-carrito"
    document.body.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-agregar-carrito');
        if (btn && !btn.disabled) {
            e.preventDefault();
            const id = btn.getAttribute('data-btn-producto-id');
            const nombre = btn.getAttribute('data-nombre');
            const precio = btn.getAttribute('data-precio');
            const stock = btn.getAttribute('data-stock-total');
            const imagen = btn.getAttribute('data-imagen');

            agregarAlCarrito(id, nombre, precio, stock, imagen);
        }
    });
});
