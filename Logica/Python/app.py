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

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir, os.pardir))
app = Flask(__name__)


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
