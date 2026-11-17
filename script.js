// Simulador de microaspersión - PARTE GRÁFICA (JavaScript)
// Los cálculos los hace Python (app.py) a través de /api/calcular

// Muestra los resultados que devuelve Python
function mostrarResultados(r) {
  return `
    <strong>Presión hidrostática:</strong> ${r.presion_pa.toFixed(2)} Pa ≈ ${r.presion_bar.toFixed(3)} bar<br>
    <strong>Velocidad de salida:</strong> ${r.velocidad.toFixed(2)} m/s<br>
    <strong>Área por orificio:</strong> ${r.area_orificio.toExponential(2)} m²<br>
    <strong>Caudal por orificio:</strong> ${r.caudal_orificio_ls.toFixed(4)} L/s<br>
    <strong>Caudal total (${r.orificios} orificios):</strong> ${r.caudal_total_ls.toFixed(4)} L/s<br>
    <strong>Agua acumulada en ${r.tiempo} s:</strong> ${r.agua_total_l.toFixed(3)} L<br>
    <strong>Distribución por m²:</strong> ${r.distribucion_l_m2.toFixed(5)} L/m²`;
}

// Genera la gráfica radar con Chart.js
function generarGraficaTornillo(r) {
  const ctx = document.getElementById("graficaTornillo").getContext("2d");

  // Destruir gráfico anterior para evitar solapamientos
  if (window.grafico) {
    window.grafico.destroy();
  }

  window.grafico = new Chart(ctx, {
    type: "radar",
    data: {
      labels: ["Caudal Total (L/s)", "Agua Total (L)", "Distribución (L/m²)"],
      datasets: [{
        label: "Tornillo Aéreo",
        data: [r.caudal_total_ls, r.agua_total_l, r.distribucion_l_m2],
        backgroundColor: "rgba(54, 162, 235, 0.4)",
        borderColor: "rgba(54, 162, 235, 1)",
        pointBackgroundColor: "rgba(54, 162, 235, 1)",
        pointBorderColor: "#fff",
        pointHoverBackgroundColor: "#fff",
        pointHoverBorderColor: "rgba(54, 162, 235, 1)"
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: { display: true, text: "Resultados del Tornillo Aéreo" }
      },
      scales: {
        r: {
          beginAtZero: true,
          ticks: { display: false },
          pointLabels: { font: { size: 14 } },
          grid: { color: "rgba(0, 0, 0, 0.1)" }
        }
      }
    }
  });
}

// Envío del formulario -> llama a Python
document.getElementById("formSimulador").addEventListener("submit", async function (e) {
  e.preventDefault();

  const datos = {
    area: parseFloat(document.getElementById("area").value),
    altura: parseFloat(document.getElementById("altura").value),
    orificios: parseInt(document.getElementById("orificios").value),
    radio: parseFloat(document.getElementById("radio").value),
    tiempo: parseFloat(document.getElementById("tiempo").value)
  };

  // Validación básica en el navegador
  if (Object.values(datos).some(v => isNaN(v) || v <= 0)) {
    document.getElementById("resultados").innerHTML =
      "Por favor, introduce valores válidos y mayores que cero.";
    return;
  }

  try {
    const respuesta = await fetch("/api/calcular", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos)
    });
    const resultado = await respuesta.json();

    if (!respuesta.ok) {
      document.getElementById("resultados").innerHTML = resultado.error;
      return;
    }

    document.getElementById("resultados").innerHTML = mostrarResultados(resultado);
    generarGraficaTornillo(resultado);

    // Guardar datos en localStorage
    localStorage.setItem("simuladorData", JSON.stringify(datos));
  } catch (err) {
    document.getElementById("resultados").innerHTML =
      "No se pudo conectar con el servidor de Python. ¿Está corriendo app.py?";
  }
});

// Al cargar la página, restaurar valores desde localStorage
window.addEventListener("DOMContentLoaded", () => {
  const data = JSON.parse(localStorage.getItem("simuladorData"));
  if (data) {
    document.getElementById("area").value = data.area;
    document.getElementById("altura").value = data.altura;
    document.getElementById("orificios").value = data.orificios;
    document.getElementById("radio").value = data.radio;
    document.getElementById("tiempo").value = data.tiempo;
  }
});
