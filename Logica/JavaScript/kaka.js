// kaka.js - PARTE VISUAL (JavaScript)
// Toda la lógica (usuarios, terrenos, aspersor) vive en Python (app.py).
// Este archivo solo maneja la pantalla y llama a la API con fetch.

// ---------------------------------------------------------------
//  Utilidades
// ---------------------------------------------------------------
const COLORES = { exito: "green", advertencia: "orange", error: "red" };

async function api(url, metodo = "GET", cuerpo = null) {
    try {
        const r = await fetch(url, {
            method: metodo,
            headers: { "Content-Type": "application/json" },
            body: cuerpo ? JSON.stringify(cuerpo) : undefined
        });
        const data = await r.json().catch(() => ({}));
        return { ...data, httpOk: r.ok };
    } catch (err) {
        return {
            ok: false,
            tipo: "error",
            mensaje: "No se pudo conectar con el servidor de Python. ¿Está corriendo app.py?"
        };
    }
}

function mostrarMensaje(elemento, texto, tipo) {
    if (!elemento) return;
    elemento.textContent = texto;
    elemento.style.color = COLORES[tipo] || "black";
}

function escapar(texto) {
    const d = document.createElement("div");
    d.textContent = texto;
    return d.innerHTML;
}

function mostrarSeccion(idSeccion) {
    document.querySelectorAll(".main-container").forEach(c => {
        c.classList.add("hidden");
        c.classList.remove("visible");
    });
    const destino = document.getElementById(idSeccion);
    if (destino) {
        destino.classList.remove("hidden");
        destino.classList.add("visible");
    } else {
        console.error(`Sección con ID '${idSeccion}' no encontrada.`);
    }
}

// ---------------------------------------------------------------
//  Panel Administrador
// ---------------------------------------------------------------
async function actualizarPanelAdmin() {
    const datos = await api("/api/admin/datos");
    if (!datos.usuarios) return;

    // Lista de usuarios
    const listaUsuarios = document.getElementById("listaUsuarios");
    if (listaUsuarios) {
        listaUsuarios.innerHTML = "<h4>Lista de Usuarios:</h4><ul>" +
            datos.usuarios.map(u => `<li>${escapar(u.nombre)} (Rol: ${escapar(u.rol)})</li>`).join("") +
            "</ul>";
    }

    // Lista de terrenos
    const listaTerrenos = document.getElementById("listaTerrenos");
    if (listaTerrenos) {
        if (datos.terrenos.length === 0) {
            listaTerrenos.innerHTML = "<p>No hay terrenos registrados.</p>";
        } else {
            listaTerrenos.innerHTML = "<h4>Lista de Terrenos:</h4><ul>" +
                datos.terrenos.map(t =>
                    `<li>ID: ${t.id}, Ancho: ${t.ancho}m, Largo: ${t.largo}m, Área: ${t.area}m² ` +
                    `${t.asignadoA ? `(Asignado a: ${escapar(t.asignadoA)})` : ""}</li>`
                ).join("") + "</ul>";
        }
    }

    // Selects de asignación
    const selCampesino = document.getElementById("selectCampesinoAsignar");
    const selTerreno = document.getElementById("selectTerrenoAsignar");
    if (selCampesino && selTerreno) {
        selCampesino.innerHTML = '<option value="">Seleccione Campesino</option>';
        selTerreno.innerHTML = '<option value="">Seleccione Terreno</option>';

        datos.usuarios.filter(u => u.rol === "campesino").forEach(c => {
            const op = document.createElement("option");
            op.value = c.nombre;
            op.textContent = c.nombre;
            selCampesino.appendChild(op);
        });

        datos.terrenos.forEach(t => {
            const op = document.createElement("option");
            op.value = t.id;
            op.textContent = `${t.id} (Área: ${t.area}m²) ${t.asignadoA ? `(Asignado a: ${t.asignadoA})` : ""}`;
            selTerreno.appendChild(op);
        });
    }
}

async function accederPanelAdmin(usuario) {
    document.getElementById("adminUsername").textContent = usuario.nombre;
    document.getElementById("adminUserRole").textContent = usuario.rol;
    await actualizarPanelAdmin();
    mostrarSeccion("adminSection");
}

// ---------------------------------------------------------------
//  Panel Campesino
// ---------------------------------------------------------------
function pintarPanelCampesino(c) {
    document.getElementById("campesinoUsername").textContent = c.nombre;
    document.getElementById("campesinoUserRole").textContent = c.rol;
    document.getElementById("infoTerrenoCampesino").textContent = c.terreno
        ? `ID: ${c.terreno.id}, Área: ${c.terreno.area}m²`
        : "Ninguno asignado.";
    document.getElementById("estadoAspersorCampesino").textContent =
        c.aspersorEncendido ? "ENCENDIDO" : "APAGADO";
}

async function accederPanelCampesino() {
    const datos = await api("/api/campesino/panel");
    if (!datos.nombre) {
        mostrarSeccion("welcomeSection");
        return;
    }
    pintarPanelCampesino(datos);
    mostrarSeccion("campesinoSection");
}

async function controlarAspersor(accion) {
    const r = await api("/api/campesino/aspersor", "POST", { accion });
    if (r.aspersorEncendido !== undefined) {
        document.getElementById("estadoAspersorCampesino").textContent =
            r.aspersorEncendido ? "ENCENDIDO" : "APAGADO";
    }
    alert(r.mensaje);
}

// ---------------------------------------------------------------
//  Sesión
// ---------------------------------------------------------------
async function cerrarSesion() {
    await api("/api/logout", "POST");
    const formLogin = document.getElementById("formLogin");
    if (formLogin) formLogin.reset();
    const mensajeLogin = document.getElementById("mensajeLogin");
    if (mensajeLogin) mensajeLogin.textContent = "";
    mostrarSeccion("welcomeSection");
    alert("¡Has cerrado sesión!");
}

// ---------------------------------------------------------------
//  Formularios
// ---------------------------------------------------------------
function conectarLogin() {
    const form = document.getElementById("formLogin");
    const mensaje = document.getElementById("mensajeLogin");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const r = await api("/api/login", "POST", {
            nombre: document.getElementById("loginNombre").value,
            password: document.getElementById("loginContrasena").value
        });
        mostrarMensaje(mensaje, r.mensaje, r.tipo);
        if (!r.ok) return;

        form.reset();
        alert(`¡Bienvenido, ${r.usuario.nombre}! Has accedido.`);
        if (r.usuario.rol === "administrador") {
            accederPanelAdmin(r.usuario);
        } else {
            pintarPanelCampesino(r.usuario);
            mostrarSeccion("campesinoSection");
        }
    });
}

function conectarRegistro() {
    const form = document.getElementById("formCrearUsuario");
    const mensaje = document.getElementById("mensajeRegistro");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const r = await api("/api/registro", "POST", {
            nombre: document.getElementById("nombreUsuario").value,
            password: document.getElementById("contrasenaUsuario").value
        });
        mostrarMensaje(mensaje, r.mensaje, r.tipo);
        if (r.ok) form.reset();
    });
}

function conectarCrearUsuarioAdmin() {
    const form = document.getElementById("formAdminCrearUsuario");
    const mensaje = document.getElementById("mensajeAdminCrearUsuario");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const r = await api("/api/admin/usuarios", "POST", {
            nombre: document.getElementById("adminNombreUsuario").value,
            password: document.getElementById("adminContrasenaUsuario").value,
            rol: document.getElementById("adminRolUsuario").value
        });
        mostrarMensaje(mensaje, r.mensaje, r.tipo);
        if (r.ok) {
            form.reset();
            actualizarPanelAdmin();
        }
    });
}

function conectarCrearTerreno() {
    const form = document.getElementById("formAdminCrearTerreno");
    const mensaje = document.getElementById("mensajeAdminCrearTerreno");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const r = await api("/api/admin/terrenos", "POST", {
            ancho: parseFloat(document.getElementById("adminAnchoTerreno").value),
            largo: parseFloat(document.getElementById("adminLargoTerreno").value)
        });
        mostrarMensaje(mensaje, r.mensaje, r.tipo);
        if (r.ok) {
            form.reset();
            actualizarPanelAdmin();
        }
    });
}

function conectarAsignarTerreno() {
    const form = document.getElementById("formAdminAsignarTerreno");
    const mensaje = document.getElementById("mensajeAsignarTerreno");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const r = await api("/api/admin/asignar", "POST", {
            campesino: document.getElementById("selectCampesinoAsignar").value,
            terreno: document.getElementById("selectTerrenoAsignar").value
        });
        mostrarMensaje(mensaje, r.mensaje, r.tipo);
        if (r.ok) actualizarPanelAdmin();
    });
}

// ---------------------------------------------------------------
//  Inicio
// ---------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    conectarLogin();
    conectarRegistro();
    conectarCrearUsuarioAdmin();
    conectarCrearTerreno();
    conectarAsignarTerreno();

    const clic = (id, fn) => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("click", fn);
    };

    clic("showLoginBtn", () => mostrarSeccion("loginSection"));
    clic("showRegisterBtn", () => mostrarSeccion("registerSection"));
    clic("backToWelcomeFromLogin", () => mostrarSeccion("welcomeSection"));
    clic("backToWelcomeFromRegister", () => mostrarSeccion("welcomeSection"));
    clic("logoutAdminBtn", cerrarSesion);
    clic("logoutCampesinoBtn", cerrarSesion);
    clic("btnEncenderAspersor", () => controlarAspersor("encender"));
    clic("btnApagarAspersor", () => controlarAspersor("apagar"));

    mostrarSeccion("welcomeSection");
});
