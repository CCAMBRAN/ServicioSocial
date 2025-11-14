/**
 * app.js - Lógica principal de la aplicación
 */

// Mostrar sección específica
function mostrarSeccion(seccionId) {
    // Ocultar todas las secciones
    document.querySelectorAll(".seccion").forEach(seccion => {
        seccion.classList.remove("activa");
    });

    // Mostrar sección seleccionada
    const seccion = document.getElementById(seccionId);
    if (seccion) {
        seccion.classList.add("activa");
        
        // Ejecutar acciones específicas por sección
        if (seccionId === "seguros") {
            cargarSeguros();
        } else if (seccionId === "dashboard") {
            cargarDashboard();
        }
    }

    // Scroll al inicio
    window.scrollTo(0, 0);
}

/**
 * Cargar lista de seguros
 */
async function cargarSeguros() {
    const listaSeguros = document.getElementById("seguros-list");
    listaSeguros.innerHTML = '<div class="loading">Cargando seguros...</div>';

    try {
        const seguros = await API.obtenerSeguros();
        
        if (seguros.length === 0) {
            listaSeguros.innerHTML = '<div class="alert alert-info">No hay seguros disponibles</div>';
            return;
        }

        listaSeguros.innerHTML = seguros.map(seguro => crearTarjetaSeguro(seguro)).join("");
    } catch (error) {
        listaSeguros.innerHTML = `<div class="alert alert-danger">Error al cargar seguros: ${error.message}</div>`;
    }
}

/**
 * Crear HTML de tarjeta de seguro
 */
function crearTarjetaSeguro(seguro) {
    const tipoBadge = seguro.tipo || "basico";
    const beneficios = (seguro.beneficios || "").split("\n").filter(b => b.trim());

    return `
        <div class="seguro-card">
            <span class="seguro-badge ${tipoBadge}">${seguro.tipo || "Básico"}</span>
            <h3>${seguro.nombre || "Sin nombre"}</h3>
            <p>${seguro.descripcion || "Sin descripción"}</p>
            
            <div class="seguro-price">$${(seguro.precio || 0).toFixed(2)}</div>
            <p class="seguro-cuota">Cuota mensual: $${(seguro.cuota_mensual || 0).toFixed(2)}</p>
            
            <div class="seguro-features">
                <li>Cobertura: $${(seguro.cobertura || 0).toLocaleString()}</li>
                <li>Duración: ${seguro.duracion_meses || 0} meses</li>
                ${beneficios.map(b => `<li>${b}</li>`).join("")}
            </div>
            
            <button class="btn btn-primary btn-block btn-sm" onclick="comprarSeguro('${seguro.id || ''}', '${seguro.nombre || ''}', ${seguro.precio || 0})">
                Comprar Ahora
            </button>
        </div>
    `;
}

/**
 * Comprar un seguro
 */
function comprarSeguro(seguroId, nombreSeguro, precio) {
    const usuario = Storage.obtenerUsuario();

    if (!usuario) {
        alert("Debes registrarte primero para comprar un seguro");
        mostrarSeccion("registro");
        return;
    }

    alert(`Compra de "${nombreSeguro}" por $${precio.toFixed(2)} iniciada.\n\nEsta es una demostración. En producción procesaría el pago.`);
}

/**
 * Cargar dashboard del usuario
 */
async function cargarDashboard() {
    const usuario = Storage.obtenerUsuario();
    const dashboardContent = document.getElementById("dashboard-content");

    if (!usuario) {
        dashboardContent.innerHTML = `
            <div class="alert alert-info">
                ℹ️ Regístrate primero para acceder al dashboard
            </div>
            <button class="btn btn-primary" onclick="mostrarSeccion('registro')">Ir a Registro</button>
        `;
        return;
    }

    dashboardContent.innerHTML = `
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <h3>Nombre</h3>
                <p>${usuario.nombre}</p>
            </div>
            <div class="dashboard-card">
                <h3>Email</h3>
                <p>${usuario.email}</p>
            </div>
            <div class="dashboard-card">
                <h3>Saldo</h3>
                <p>$${(usuario.saldo || 0).toFixed(2)}</p>
            </div>
            <div class="dashboard-card">
                <h3>Teléfono</h3>
                <p>${usuario.telefono || "No registrado"}</p>
            </div>
        </div>

        <div style="margin-top: 2rem; text-align: center;">
            <button class="btn btn-primary btn-sm" onclick="mostrarSeccion('seguros')">Ver Seguros</button>
            <button class="btn btn-primary btn-sm" onclick="cerrarSesion()">Cerrar Sesión</button>
        </div>
    `;
}

/**
 * Manejar formulario de registro
 */
document.addEventListener("DOMContentLoaded", function () {
    const formRegistro = document.getElementById("form-registro");

    if (formRegistro) {
        formRegistro.addEventListener("submit", async function (e) {
            e.preventDefault();

            const nombre = document.getElementById("nombre").value.trim();
            const email = document.getElementById("email").value.trim();
            const telefono = document.getElementById("telefono").value.trim();
            const mensajeDiv = document.getElementById("mensaje-registro");

            if (!nombre || !email) {
                mensajeDiv.textContent = "Por favor completa todos los campos requeridos";
                mensajeDiv.classList.add("error");
                return;
            }

            try {
                mensajeDiv.textContent = "Creando cuenta...";
                mensajeDiv.className = "mensaje info";

                const usuario = await API.crearUsuario({
                    nombre,
                    email,
                    telefono
                });

                // Guardar usuario en localStorage
                Storage.guardarUsuario(usuario);

                mensajeDiv.textContent = `¡Cuenta creada exitosamente! Bienvenido, ${usuario.nombre}`;
                mensajeDiv.className = "mensaje success";

                // Limpiar formulario
                formRegistro.reset();

                // Redirigir al dashboard después de 2 segundos
                setTimeout(() => {
                    mostrarSeccion("dashboard");
                }, 2000);

            } catch (error) {
                mensajeDiv.textContent = `Error: ${error.message}`;
                mensajeDiv.className = "mensaje error";
                console.error("Error al registrar:", error);
            }
        });
    }
});

/**
 * Cerrar sesión
 */
function cerrarSesion() {
    if (confirm("¿Estás seguro que deseas cerrar sesión?")) {
        Storage.eliminarUsuario();
        mostrarSeccion("inicio");
        alert("Sesión cerrada correctamente");
    }
}

/**
 * Verificar si hay usuario en sesión al cargar
 */
document.addEventListener("DOMContentLoaded", function () {
    const usuario = Storage.obtenerUsuario();
    
    // Ejemplo: mostrar nombre del usuario en la navbar si existe
    // Esto es opcional, puedes expandir esto según necesites
    if (usuario) {
        console.log(`Usuario en sesión: ${usuario.nombre}`);
    }
});
