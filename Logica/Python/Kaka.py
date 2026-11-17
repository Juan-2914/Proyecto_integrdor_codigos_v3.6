"""
Sistema de Gestión Agrícola - PARTE LÓGICA (Python + Flask)

Reemplaza la lógica que estaba en JS/kaka.js (Terreno, Usuario,
Administrador, Campesino). El navegador solo muestra y envía datos.

Instalación y ejecución:
    pip install flask
    python app.py
Abre: http://127.0.0.1:5000

Coloca este archivo en la RAÍZ del proyecto, junto a las carpetas
CSS, HTML y JS (Proyecto_integrdor_codigos_v3.6/app.py), y reemplaza
JS/kaka.js por el nuevo kaka.js.
"""
import os
from functools import wraps

from flask import Flask, jsonify, redirect, request, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir, os.pardir))

app = Flask(__name__)
app.secret_key = "cambia-esta-clave-secreta"  # necesaria para las sesiones


# =====================================================================
#  MODELO
# =====================================================================

class Terreno:
    PREFIJO = "T-"
    _ultimo_id = 0
    todos = []

    def __init__(self, ancho, largo):
        if ancho <= 0 or largo <= 0:
            raise ValueError("Las dimensiones del terreno deben ser positivas.")
        Terreno._ultimo_id += 1
        self.ancho = ancho
        self.largo = largo
        self.id = f"{Terreno.PREFIJO}{Terreno._ultimo_id:02d}"
        self.aspersor_activo = False
        self.humedad = 0
        self.asignado_a = None
        Terreno.todos.append(self)

    @property
    def area(self):
        return round(self.ancho * self.largo, 2)

    def toggle_aspersor(self):
        self.aspersor_activo = not self.aspersor_activo

    def set_humedad(self, nueva):
        if 0 <= nueva <= 100:
            self.humedad = nueva
            return True
        return False

    @staticmethod
    def buscar(id_terreno):
        return next((t for t in Terreno.todos if t.id == id_terreno), None)

    def a_dict(self):
        return {
            "id": self.id,
            "ancho": self.ancho,
            "largo": self.largo,
            "area": self.area,
            "aspersorActivo": self.aspersor_activo,
            "humedad": self.humedad,
            "asignadoA": self.asignado_a,
        }


class Usuario:
    usuarios = []

    def __init__(self, nombre, password, rol):
        self.nombre = nombre
        self.__password_hash = generate_password_hash(password)  # privado
        self.rol = rol

    def verificar_contrasena(self, ingresada):
        return check_password_hash(self.__password_hash, ingresada)

    def a_dict(self):
        return {"nombre": self.nombre, "rol": self.rol}

    @staticmethod
    def buscar(nombre):
        return next((u for u in Usuario.usuarios if u.nombre == nombre), None)

    @staticmethod
    def crear_usuario(rol, nombre, password):
        if Usuario.buscar(nombre):
            return None
        rol = rol.lower()
        if rol in ("administrador", "admin"):
            nuevo = Administrador(nombre, password)
        elif rol == "campesino":
            nuevo = Campesino(nombre, password)
        else:
            return None
        Usuario.usuarios.append(nuevo)
        return nuevo

    @staticmethod
    def autenticar(nombre, password):
        u = Usuario.buscar(nombre)
        return u if u and u.verificar_contrasena(password) else None


class Administrador(Usuario):
    def __init__(self, nombre, password):
        super().__init__(nombre, password, "administrador")


class Campesino(Usuario):
    def __init__(self, nombre, password):
        super().__init__(nombre, password, "campesino")
        self.terreno_asignado = None

    @property
    def aspersor_encendido(self):
        return bool(self.terreno_asignado and self.terreno_asignado.aspersor_activo)

    def encender_aspersor(self):
        if not self.terreno_asignado:
            return False, "No tienes un terreno asignado para encender el aspersor."
        if self.terreno_asignado.aspersor_activo:
            return False, "El aspersor ya está encendido."
        self.terreno_asignado.toggle_aspersor()
        return True, f"Aspersor de {self.nombre} en terreno {self.terreno_asignado.id} encendido."

    def apagar_aspersor(self):
        if not self.terreno_asignado:
            return False, "No tienes un terreno asignado para apagar el aspersor."
        if not self.terreno_asignado.aspersor_activo:
            return False, "El aspersor ya está apagado."
        self.terreno_asignado.toggle_aspersor()
        return True, f"Aspersor de {self.nombre} en terreno {self.terreno_asignado.id} apagado."

    def a_dict(self):
        d = super().a_dict()
        d["terreno"] = self.terreno_asignado.a_dict() if self.terreno_asignado else None
        d["aspersorEncendido"] = self.aspersor_encendido
        return d


# Datos iniciales (igual que en kaka.js)
Usuario.crear_usuario("administrador", "Jsnavaro", "kaka")
Usuario.crear_usuario("campesino", "campesino1", "campesino123")
Usuario.crear_usuario("campesino", "juanito", "pass123")


# =====================================================================
#  UTILIDADES
# =====================================================================

def respuesta(ok, mensaje, tipo=None, status=200, **extra):
    """tipo: 'exito' | 'advertencia' | 'error' (el JS lo usa para el color)."""
    tipo = tipo or ("exito" if ok else "error")
    return jsonify({"ok": ok, "mensaje": mensaje, "tipo": tipo, **extra}), status


def usuario_actual():
    return Usuario.buscar(session.get("usuario"))


def requiere_rol(rol):
    def decorador(fn):
        @wraps(fn)
        def envoltura(*args, **kwargs):
            u = usuario_actual()
            if not u or u.rol != rol:
                return respuesta(False, f"Acceso solo para {rol}.", status=403)
            return fn(u, *args, **kwargs)
        return envoltura
    return decorador


def datos_json():
    return request.get_json(silent=True) or {}


# =====================================================================
#  ARCHIVOS ESTÁTICOS (HTML / CSS / JS del proyecto)
# =====================================================================

@app.route("/")
def inicio():
    return send_from_directory(os.path.join(PROJECT_ROOT, "Vista"), "INDEX.html")


@app.route("/Vista/HTML/<path:archivo>")
def estaticos_html(archivo):
    return send_from_directory(os.path.join(PROJECT_ROOT, "Vista", "HTML"), archivo)


@app.route("/Vista/CSS/<path:archivo>")
def estaticos_css(archivo):
    return send_from_directory(os.path.join(PROJECT_ROOT, "Vista", "CSS"), archivo)


@app.route("/Logica/JavaScript/<path:archivo>")
def estaticos_js(archivo):
    return send_from_directory(os.path.join(PROJECT_ROOT, "Logica", "JavaScript"), archivo)


# =====================================================================
#  API: SESIÓN Y REGISTRO
# =====================================================================

@app.route("/api/login", methods=["POST"])
def login():
    d = datos_json()
    u = Usuario.autenticar(str(d.get("nombre", "")), str(d.get("password", "")))
    if not u:
        return respuesta(False, "Nombre de usuario o contraseña inválidos", status=401)
    session["usuario"] = u.nombre
    return respuesta(True, f"Bienvenido, {u.nombre} ({u.rol})", usuario=u.a_dict())


@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("usuario", None)
    return respuesta(True, "Sesión cerrada.")


@app.route("/api/registro", methods=["POST"])
def registro():
    d = datos_json()
    nuevo = Usuario.crear_usuario("campesino", str(d.get("nombre", "")).strip(), str(d.get("password", "")))
    if not nuevo:
        return respuesta(False, "Error al registrar el campesino (posiblemente ya existe).", status=400)
    return respuesta(True, "Campesino registrado con éxito")


# =====================================================================
#  API: ADMINISTRADOR
# =====================================================================

@app.route("/api/admin/datos")
@requiere_rol("administrador")
def admin_datos(_admin):
    return jsonify({
        "usuarios": [u.a_dict() for u in Usuario.usuarios],
        "terrenos": [t.a_dict() for t in Terreno.todos],
    })


@app.route("/api/admin/usuarios", methods=["POST"])
@requiere_rol("administrador")
def admin_crear_usuario(_admin):
    d = datos_json()
    nombre = str(d.get("nombre", "")).strip()
    rol = str(d.get("rol", ""))
    nuevo = Usuario.crear_usuario(rol, nombre, str(d.get("password", "")))
    if not nuevo:
        return respuesta(False, "Error al crear el usuario (posiblemente ya existe).", status=400)
    return respuesta(True, f"Usuario {nombre} ({rol}) creado con éxito.")


@app.route("/api/admin/terrenos", methods=["POST"])
@requiere_rol("administrador")
def admin_crear_terreno(_admin):
    d = datos_json()
    try:
        t = Terreno(float(d.get("ancho")), float(d.get("largo")))
    except (TypeError, ValueError) as e:
        msg = str(e) if "dimensiones" in str(e) else "Ancho y largo deben ser números."
        return respuesta(False, f"Error al crear el terreno: {msg}", status=400)
    return respuesta(True, f"Terreno {t.id} (Área: {t.area}m²) creado con éxito.")


@app.route("/api/admin/asignar", methods=["POST"])
@requiere_rol("administrador")
def admin_asignar(_admin):
    d = datos_json()
    campesino = Usuario.buscar(str(d.get("campesino", "")))
    terreno = Terreno.buscar(str(d.get("terreno", "")))

    if not (isinstance(campesino, Campesino) and terreno):
        return respuesta(False, "Error: Campesino o Terreno no encontrado.", status=404)
    if terreno.asignado_a:
        return respuesta(False, f"El terreno {terreno.id} ya está asignado a {terreno.asignado_a}.",
                         tipo="advertencia", status=409)
    if campesino.terreno_asignado:
        return respuesta(False, f"El campesino {campesino.nombre} ya tiene asignado el terreno "
                                f"{campesino.terreno_asignado.id}.", tipo="advertencia", status=409)

    campesino.terreno_asignado = terreno
    terreno.asignado_a = campesino.nombre
    return respuesta(True, f"Terreno {terreno.id} asignado a {campesino.nombre} con éxito.")


# =====================================================================
#  API: CAMPESINO
# =====================================================================

@app.route("/api/campesino/panel")
@requiere_rol("campesino")
def campesino_panel(campesino):
    return jsonify(campesino.a_dict())


@app.route("/api/campesino/aspersor", methods=["POST"])
@requiere_rol("campesino")
def campesino_aspersor(campesino):
    accion = datos_json().get("accion")
    if accion == "encender":
        ok, msg = campesino.encender_aspersor()
    elif accion == "apagar":
        ok, msg = campesino.apagar_aspersor()
    else:
        return respuesta(False, "Acción no válida.", status=400)
    return respuesta(ok, msg, tipo="exito" if ok else "advertencia",
                     aspersorEncendido=campesino.aspersor_encendido)


if __name__ == "__main__":
    app.run(debug=True)
