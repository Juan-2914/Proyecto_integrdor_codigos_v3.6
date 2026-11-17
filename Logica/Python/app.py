"""
Simulador de microaspersión - PARTE LÓGICA (Python + Flask)

Ejecución:
    pip install flask
    python app.py
Luego abre http://127.0.0.1:5000 en el navegador.

Este archivo debe estar en la misma carpeta que script.js
"""
import math
import os
import sqlite3
from functools import wraps

from flask import Flask, jsonify, request, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir, os.pardir))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "agricultura.db")
app = Flask(__name__)
app.config["SECRET_KEY"] = "agricultura-2026-seguro-local"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS terrenos (
            id TEXT PRIMARY KEY,
            ancho REAL NOT NULL,
            largo REAL NOT NULL,
            aspersor_activo INTEGER NOT NULL DEFAULT 0,
            humedad INTEGER NOT NULL DEFAULT 0,
            asignado_a TEXT DEFAULT NULL
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


class MicroAspersion:
    """Encapsula los cálculos del sistema de microaspersión."""

    G = 9.81      # Aceleración gravitatoria (m/s²)
    RHO = 1000    # Densidad del agua (kg/m³)

    def __init__(self, area, altura, orificios, radio, tiempo):
        self.area = area            # m²
        self.altura = altura        # m
        self.orificios = orificios  # unidades
        self.radio = radio          # m
        self.tiempo = tiempo        # s

    def calcular_presion(self):
        """Presión hidrostática (Pa)."""
        return self.RHO * self.G * self.altura

    def calcular_velocidad_salida(self):
        """Velocidad de salida según Torricelli (m/s)."""
        return math.sqrt(2 * self.G * self.altura)

    def calcular_area_orificio(self):
        """Área de un orificio circular (m²)."""
        return math.pi * self.radio ** 2

    def calcular_caudal_por_orificio(self):
        """Caudal por orificio (m³/s)."""
        return self.calcular_area_orificio() * self.calcular_velocidad_salida()

    def calcular_caudal_total(self):
        """Caudal total del sistema (m³/s)."""
        return self.calcular_caudal_por_orificio() * self.orificios

    def calcular_agua_total(self):
        """Volumen total de agua liberada (litros)."""
        return self.calcular_caudal_total() * self.tiempo * 1000

    def calcular_distribucion_por_m2(self):
        """Distribución de agua por metro cuadrado (L/m²)."""
        return self.calcular_agua_total() / self.area

    def resultados(self):
        """Devuelve todos los resultados en un diccionario (listo para JSON)."""
        presion = self.calcular_presion()
        return {
            "presion_pa": presion,
            "presion_bar": presion / 100000,
            "velocidad": self.calcular_velocidad_salida(),
            "area_orificio": self.calcular_area_orificio(),
            "caudal_orificio_ls": self.calcular_caudal_por_orificio() * 1000,
            "caudal_total_ls": self.calcular_caudal_total() * 1000,
            "agua_total_l": self.calcular_agua_total(),
            "distribucion_l_m2": self.calcular_distribucion_por_m2(),
            "orificios": self.orificios,
            "tiempo": self.tiempo,
        }


# ----------------------------- RUTAS -----------------------------

@app.route("/")
def index():
    return send_from_directory(os.path.join(PROJECT_ROOT, "Vista"), "INDEX.html")


@app.route("/Vista/INDEX.html")
def index_html():
    return send_from_directory(os.path.join(PROJECT_ROOT, "Vista"), "INDEX.html")


@app.route("/Vista/HTML/<path:filename>")
def html_files(filename):
    return send_from_directory(os.path.join(PROJECT_ROOT, "Vista", "HTML"), filename)


@app.route("/Vista/CSS/<path:filename>")
def css_files(filename):
    return send_from_directory(os.path.join(PROJECT_ROOT, "Vista", "CSS"), filename)


@app.route("/CSS/<path:filename>")
def css_root_files(filename):
    return send_from_directory(os.path.join(PROJECT_ROOT, "Vista", "CSS"), filename)


@app.route("/Logica/JavaScript/<path:filename>")
def js_files(filename):
    return send_from_directory(os.path.join(PROJECT_ROOT, "Logica", "JavaScript"), filename)


@app.route("/script.js")
def script():
    return send_from_directory(os.path.join(PROJECT_ROOT, "Logica", "JavaScript"), "script.js")


@app.route("/simulador.js")
def simulador_js():
    return send_from_directory(os.path.join(PROJECT_ROOT, "Logica", "JavaScript"), "simulador.js")


@app.route("/kaka.js")
def kaka_js():
    return send_from_directory(os.path.join(PROJECT_ROOT, "Logica", "JavaScript"), "kaka.js")


@app.route("/api/calcular", methods=["POST"])
def calcular():
    datos = request.get_json(silent=True) or {}
    try:
        area = float(datos["area"])
        altura = float(datos["altura"])
        orificios = int(datos["orificios"])
        radio = float(datos["radio"])
        tiempo = float(datos["tiempo"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Datos incompletos o inválidos."}), 400

    if min(area, altura, orificios, radio, tiempo) <= 0:
        return jsonify({"error": "Introduce valores válidos y mayores que cero."}), 400

    sistema = MicroAspersion(area, altura, orificios, radio, tiempo)
    return jsonify(sistema.resultados())


# ----------------------------- MODELO DE ROLES -----------------------------

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
        self._guardar_en_bd()
        Terreno.todos = Terreno.listar()

    @classmethod
    def _from_db_row(cls, row):
        terreno = cls.__new__(cls)
        terreno.ancho = row["ancho"]
        terreno.largo = row["largo"]
        terreno.id = row["id"]
        terreno.aspersor_activo = bool(row["aspersor_activo"])
        terreno.humedad = row["humedad"]
        terreno.asignado_a = row["asignado_a"]
        try:
            Terreno._ultimo_id = max(Terreno._ultimo_id, int(terreno.id.split("-")[-1]))
        except (ValueError, TypeError):
            pass
        return terreno

    @staticmethod
    def listar():
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT id, ancho, largo, aspersor_activo, humedad, asignado_a FROM terrenos ORDER BY id"
        ).fetchall()
        conn.close()
        return [Terreno._from_db_row(row) for row in rows]

    def _guardar_en_bd(self):
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO terrenos (id, ancho, largo, aspersor_activo, humedad, asignado_a) VALUES (?, ?, ?, ?, ?, ?)",
            (self.id, self.ancho, self.largo, int(self.aspersor_activo), self.humedad, self.asignado_a),
        )
        conn.commit()
        conn.close()

    def guardar_cambios(self):
        conn = get_db_connection()
        conn.execute(
            "UPDATE terrenos SET ancho = ?, largo = ?, aspersor_activo = ?, humedad = ?, asignado_a = ? WHERE id = ?",
            (self.ancho, self.largo, int(self.aspersor_activo), self.humedad, self.asignado_a, self.id),
        )
        conn.commit()
        conn.close()
        Terreno.todos = Terreno.listar()

    @property
    def area(self):
        return round(self.ancho * self.largo, 2)

    def toggle_aspersor(self):
        self.aspersor_activo = not self.aspersor_activo
        self.guardar_cambios()

    def set_humedad(self, nueva):
        if 0 <= nueva <= 100:
            self.humedad = nueva
            self.guardar_cambios()
            return True
        return False

    @staticmethod
    def buscar(id_terreno):
        return next((t for t in Terreno.todos if t.id == id_terreno), None)

    @staticmethod
    def actualizar(id_terreno, ancho, largo):
        terreno = Terreno.buscar(id_terreno)
        if not terreno:
            return None
        if ancho <= 0 or largo <= 0:
            return None
        terreno.ancho = float(ancho)
        terreno.largo = float(largo)
        terreno.guardar_cambios()
        return terreno

    @staticmethod
    def eliminar(id_terreno):
        terreno = Terreno.buscar(id_terreno)
        if not terreno:
            return False
        conn = get_db_connection()
        conn.execute("DELETE FROM terrenos WHERE id = ?", (id_terreno,))
        conn.execute("UPDATE terrenos SET asignado_a = NULL WHERE asignado_a = ?", (terreno.asignado_a,)) if terreno.asignado_a else None
        conn.commit()
        conn.close()
        if terreno.asignado_a:
            usuario = Usuario.buscar(terreno.asignado_a)
            if usuario and hasattr(usuario, "terreno_asignado"):
                usuario.terreno_asignado = None
        Terreno.todos = Terreno.listar()
        Usuario.usuarios = Usuario.listar()
        return True

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
        self.__password_hash = generate_password_hash(password)
        self.rol = rol
        self._guardar_en_bd()
        Usuario.usuarios = Usuario.listar()

    @classmethod
    def _from_db_row(cls, row):
        rol = row["rol"]
        if rol == "administrador":
            usuario = Administrador.__new__(Administrador)
        elif rol == "campesino":
            usuario = Campesino.__new__(Campesino)
        else:
            usuario = cls.__new__(cls)
        usuario.nombre = row["nombre"]
        usuario._Usuario__password_hash = row["password_hash"]
        usuario.rol = rol
        if rol == "campesino":
            usuario.terreno_asignado = next(
                (t for t in Terreno.todos if t.asignado_a == usuario.nombre),
                None,
            )
        return usuario

    @staticmethod
    def listar():
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT nombre, password_hash, rol FROM usuarios ORDER BY nombre"
        ).fetchall()
        conn.close()
        return [Usuario._from_db_row(row) for row in rows]

    def _guardar_en_bd(self):
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO usuarios (nombre, password_hash, rol) VALUES (?, ?, ?)",
            (self.nombre, self._Usuario__password_hash, self.rol),
        )
        conn.commit()
        conn.close()

    def verificar_contrasena(self, ingresada):
        return check_password_hash(self._Usuario__password_hash, ingresada)

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
        Usuario.usuarios = Usuario.listar()
        return nuevo

    @staticmethod
    def actualizar(nombre_actual, nombre_nuevo, rol, password=None):
        nombre_actual = nombre_actual.strip()
        nombre_nuevo = nombre_nuevo.strip()
        if not nombre_actual or not nombre_nuevo:
            return None
        if nombre_actual != nombre_nuevo and Usuario.buscar(nombre_nuevo):
            return None

        usuario_actual = Usuario.buscar(nombre_actual)
        if not usuario_actual:
            return None

        rol = rol.lower()
        if rol not in ("administrador", "campesino"):
            return None

        conn = get_db_connection()
        if password and password.strip():
            nuevo_hash = generate_password_hash(password)
            conn.execute(
                "UPDATE usuarios SET nombre = ?, rol = ?, password_hash = ? WHERE nombre = ?",
                (nombre_nuevo, rol, nuevo_hash, nombre_actual),
            )
        else:
            conn.execute(
                "UPDATE usuarios SET nombre = ?, rol = ? WHERE nombre = ?",
                (nombre_nuevo, rol, nombre_actual),
            )

        if rol == "campesino":
            conn.execute(
                "UPDATE terrenos SET asignado_a = ? WHERE asignado_a = ?",
                (nombre_nuevo, nombre_actual),
            )
        else:
            conn.execute(
                "UPDATE terrenos SET asignado_a = NULL WHERE asignado_a = ?",
                (nombre_actual,),
            )
        conn.commit()
        conn.close()

        Usuario.usuarios = Usuario.listar()
        Terreno.todos = Terreno.listar()
        return Usuario.buscar(nombre_nuevo)

    @staticmethod
    def eliminar(nombre):
        nombre = nombre.strip()
        if not nombre:
            return False
        if session.get("usuario") == nombre:
            return False

        conn = get_db_connection()
        conn.execute("DELETE FROM usuarios WHERE nombre = ?", (nombre,))
        conn.execute("UPDATE terrenos SET asignado_a = NULL WHERE asignado_a = ?", (nombre,))
        conn.commit()
        conn.close()

        Usuario.usuarios = Usuario.listar()
        Terreno.todos = Terreno.listar()
        return True

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
        self._actualizar_terreno_asignado_en_bd()

    def _actualizar_terreno_asignado_en_bd(self):
        conn = get_db_connection()
        if self.terreno_asignado is None:
            conn.execute("UPDATE terrenos SET asignado_a = NULL WHERE asignado_a = ?", (self.nombre,))
        conn.commit()
        conn.close()

    def encender_aspersor(self):
        if not self.terreno_asignado:
            return False, "No tienes un terreno asignado para encender el aspersor."
        if self.terreno_asignado.aspersor_activo:
            return False, "El aspersor ya está encendido."
        self.terreno_asignado.toggle_aspersor()
        return True, f"Aspersor de {self.nombre} encendido."

    def apagar_aspersor(self):
        if not self.terreno_asignado:
            return False, "No tienes un terreno asignado para apagar el aspersor."
        if not self.terreno_asignado.aspersor_activo:
            return False, "El aspersor ya está apagado."
        self.terreno_asignado.toggle_aspersor()
        return True, f"Aspersor de {self.nombre} apagado."

    def cambiar_terreno(self, id_terreno):
        terreno = Terreno.buscar(id_terreno)
        if not terreno:
            return False, "Terreno no encontrado."
        if terreno.asignado_a and terreno.asignado_a != self.nombre:
            return False, f"El terreno {terreno.id} ya está asignado a {terreno.asignado_a}."
        if self.terreno_asignado and self.terreno_asignado.id == terreno.id:
            return True, f"Ya tienes asignado el terreno {terreno.id}."

        if self.terreno_asignado:
            self.terreno_asignado.asignado_a = None
            self.terreno_asignado.guardar_cambios()

        self.terreno_asignado = terreno
        terreno.asignado_a = self.nombre
        terreno.guardar_cambios()
        return True, f"Terreno {terreno.id} asignado a {self.nombre}."

    def a_dict(self):
        d = super().a_dict()
        d["terreno"] = self.terreno_asignado.a_dict() if self.terreno_asignado else None
        d["aspersorEncendido"] = self.aspersor_encendido
        return d

    @property
    def aspersor_encendido(self):
        return bool(self.terreno_asignado and self.terreno_asignado.aspersor_activo)


Terreno.todos = Terreno.listar()
Usuario.usuarios = Usuario.listar()

if not Usuario.buscar("Jsnavaro"):
    Usuario.crear_usuario("administrador", "Jsnavaro", "kaka")
if not Usuario.buscar("campesino1"):
    Usuario.crear_usuario("campesino", "campesino1", "campesino123")
if not Usuario.buscar("juanito"):
    Usuario.crear_usuario("campesino", "juanito", "pass123")


def respuesta(ok, mensaje, tipo=None, status=200, **extra):
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


@app.route("/api/login", methods=["POST"])
def login():
    d = datos_json()
    u = Usuario.autenticar(str(d.get("nombre", "")).strip(), str(d.get("password", "")))
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
    nombre = str(d.get("nombre", "")).strip()
    password = str(d.get("password", ""))
    nuevo = Usuario.crear_usuario("campesino", nombre, password)
    if not nuevo:
        return respuesta(False, "Error al registrar el campesino (posiblemente ya existe).", status=400)
    return respuesta(True, "Campesino registrado con éxito")


@app.route("/api/terrenos")
def listar_terrenos():
    return jsonify({"terrenos": [t.a_dict() for t in Terreno.todos]})


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
    rol = str(d.get("rol", "")).strip()
    nuevo = Usuario.crear_usuario(rol, nombre, str(d.get("password", "")))
    if not nuevo:
        return respuesta(False, "Error al crear el usuario (posiblemente ya existe).", status=400)
    return respuesta(True, f"Usuario {nombre} ({rol}) creado con éxito.")


@app.route("/api/admin/usuarios/editar", methods=["POST"])
@requiere_rol("administrador")
def admin_editar_usuario(_admin):
    d = datos_json()
    nombre_actual = str(d.get("nombreActual", "")).strip()
    nombre_nuevo = str(d.get("nombreNuevo", "")).strip()
    rol = str(d.get("rol", "")).strip()
    password = str(d.get("password", ""))

    if not nombre_actual:
        return respuesta(False, "Debes indicar el usuario a editar.", status=400)

    actualizado = Usuario.actualizar(nombre_actual, nombre_nuevo or nombre_actual, rol, password if password else None)
    if not actualizado:
        return respuesta(False, "No se pudo guardar la edición del usuario. Revisa el nombre o el rol.", status=400)

    return respuesta(True, f"Usuario {nombre_actual} actualizado correctamente.")


@app.route("/api/admin/usuarios/eliminar", methods=["POST"])
@requiere_rol("administrador")
def admin_eliminar_usuario(_admin):
    d = datos_json()
    nombre = str(d.get("nombre", "")).strip()
    if not nombre:
        return respuesta(False, "Debes indicar el usuario a eliminar.", status=400)
    if session.get("usuario") == nombre:
        return respuesta(False, "No puedes eliminar tu propio usuario desde tu sesión actual.", status=400)

    if not Usuario.eliminar(nombre):
        return respuesta(False, "No se encontró el usuario para eliminar.", status=404)

    return respuesta(True, f"Usuario {nombre} eliminado con éxito.")


@app.route("/api/admin/terrenos", methods=["POST"])
@requiere_rol("administrador")
def admin_crear_terreno(_admin):
    d = datos_json()
    try:
        terreno = Terreno(float(d.get("ancho")), float(d.get("largo")))
    except (TypeError, ValueError):
        return respuesta(False, "Ancho y largo deben ser números válidos.", status=400)
    return respuesta(True, f"Terreno {terreno.id} (Área: {terreno.area}m²) creado con éxito.")


@app.route("/api/admin/asignar", methods=["POST"])
@requiere_rol("administrador")
def admin_asignar(_admin):
    d = datos_json()
    campesino = Usuario.buscar(str(d.get("campesino", "")))
    terreno = Terreno.buscar(str(d.get("terreno", "")))

    if not (isinstance(campesino, Campesino) and terreno):
        return respuesta(False, "Error: Campesino o Terreno no encontrado.", status=404)
    if terreno.asignado_a and terreno.asignado_a != campesino.nombre:
        return respuesta(False, f"El terreno {terreno.id} ya está asignado a {terreno.asignado_a}.", tipo="advertencia", status=409)

    if campesino.terreno_asignado and campesino.terreno_asignado.id != terreno.id:
        viejo = campesino.terreno_asignado
        viejo.asignado_a = None
        viejo.guardar_cambios()

    campesino.terreno_asignado = terreno
    terreno.asignado_a = campesino.nombre
    terreno.guardar_cambios()
    return respuesta(True, f"Terreno {terreno.id} asignado a {campesino.nombre} con éxito.")


@app.route("/api/admin/terrenos/editar", methods=["POST"])
@requiere_rol("administrador")
def admin_editar_terreno(_admin):
    d = datos_json()
    terreno_id = str(d.get("id", "")).strip()
    ancho = d.get("ancho")
    largo = d.get("largo")

    try:
        ancho = float(ancho)
        largo = float(largo)
    except (TypeError, ValueError):
        return respuesta(False, "Ancho y largo deben ser números válidos.", status=400)

    actualizado = Terreno.actualizar(terreno_id, ancho, largo)
    if not actualizado:
        return respuesta(False, "No se pudo actualizar el terreno.", status=400)
    return respuesta(True, f"Terreno {terreno_id} actualizado correctamente.")


@app.route("/api/admin/terrenos/eliminar", methods=["POST"])
@requiere_rol("administrador")
def admin_eliminar_terreno(_admin):
    d = datos_json()
    terreno_id = str(d.get("id", "")).strip()
    if not terreno_id:
        return respuesta(False, "Debes indicar el terreno a eliminar.", status=400)
    if not Terreno.eliminar(terreno_id):
        return respuesta(False, "No se encontró el terreno para eliminar.", status=404)
    return respuesta(True, f"Terreno {terreno_id} eliminado con éxito.")


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
    return respuesta(ok, msg, tipo="exito" if ok else "advertencia", aspersorEncendido=campesino.aspersor_encendido)


@app.route("/api/campesino/terreno/cambiar", methods=["POST"])
@requiere_rol("campesino")
def campesino_cambiar_terreno(campesino):
    terreno_id = str(datos_json().get("terrenoId", "")).strip()
    ok, msg = campesino.cambiar_terreno(terreno_id)
    return respuesta(ok, msg, tipo="exito" if ok else "advertencia", terreno=campesino.terreno_asignado.a_dict() if campesino.terreno_asignado else None)


# ----------------------------- HTML -----------------------------

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Simulador de Microaspersión</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    body { font-family: Arial, sans-serif; max-width: 700px; margin: 30px auto; padding: 0 15px; }
    label { display: block; margin-top: 10px; }
    input { width: 100%; padding: 6px; box-sizing: border-box; }
    button { margin-top: 15px; padding: 10px 20px; cursor: pointer; }
    #resultados { margin-top: 20px; line-height: 1.8; }
  </style>
</head>
<body>
  <h1>Simulador de Microaspersión</h1>

  <form id="formSimulador">
    <label>Área a regar (m²)
      <input type="number" id="area" step="any" required>
    </label>
    <label>Altura del tanque (m)
      <input type="number" id="altura" step="any" required>
    </label>
    <label>Número de orificios
      <input type="number" id="orificios" step="1" required>
    </label>
    <label>Radio del orificio (m)
      <input type="number" id="radio" step="any" required>
    </label>
    <label>Tiempo (s)
      <input type="number" id="tiempo" step="any" required>
    </label>
    <button type="submit">Calcular</button>
  </form>

  <div id="resultados"></div>
  <canvas id="graficaTornillo"></canvas>

  <script src="/script.js"></script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
