# Sistema de Microaspersión Automatizado inspirado en el Tornillo Aéreo de Leonardo da Vinci

Este proyecto combina una simulación técnica y una pequeña aplicación web para modelar el funcionamiento de un sistema de microaspersión basado en un tornillo aéreo. Su objetivo es mostrar cómo el flujo de agua, la presión hidrostática, la velocidad de salida y la distribución del agua en el terreno pueden analizarse a través de una interfaz visual.

La aplicación está pensada para presentarse como un proyecto integrador universitario, integrando:

- lógica matemática y física del sistema
- backend con Python y Flask
- interfaz web con HTML, CSS y JavaScript
- simulación de resultados en tiempo real
- gestión básica de usuarios y terrenos

---

## Objetivo general

Diseñar y simular un sistema de microaspersión automatizado que aproveche la lógica del tornillo aéreo para distribuir agua en un terreno, evaluando variables como:

- área del terreno
- altura del depósito
- número de orificios
- radio del orificio
- tiempo de operación
- presión y caudal generado
- distribución por metro cuadrado

---

## Funcionalidades principales

- Simulación del flujo de agua y cálculo de resultados hidráulicos
- Cálculo de presión hidrostática y velocidad de salida
- Determinación de caudal por orificio y caudal total
- Estimación de volumen de agua en litros y distribución por m²
- Visualización gráfica con Chart.js
- Sistema de login básico para usuarios y administración
- Gestión de terrenos y asignación a campesinos
- Panel administrativo para crear usuarios y terrenos
- Panel campesino para controlar el aspersor

---

## Tecnologías utilizadas

- Python 3
- Flask
- JavaScript
- HTML5
- CSS3
- Chart.js

---

## Estructura del proyecto

```text
Proyecto_integrdor_codigos_v3.6/
├── app.py
├── Kaka.py
├── README.md
├── Logica/
│   ├── Python/
│   │   ├── app.py
│   │   ├── Kaka.py
│   └── JavaScript/
│       ├── kaka.js
│       ├── script.js
│       └── simulador.js
├── Vista/
│   ├── INDEX.html
│   ├── HTML/
│   │   ├── 0_inicio.html
│   │   ├── 1_expicasion.html
│   │   ├── 2_simulacion.html
│   │   └── 4_documento.html
│   └── CSS/
│       ├── estilo.css
│       └── eslilos.css
└── .git/
```

---

## Requisitos

- Python 3.9 o superior
- Flask
- Navegador web moderno

Instala Flask con:

```bash
pip install flask
```

---

## Ejecución

Desde la raíz del proyecto:

```bash
python3 app.py
```

Luego abre en el navegador:

```text
http://127.0.0.1:5000
```

También puedes arrancar la versión de lógica de usuarios con:

```bash
python3 Kaka.py
```

---

## Cómo usar la aplicación

### Página principal
La aplicación muestra una vista general del proyecto y presenta acceso a la explicación, la simulación y el documento.

### Simulación
En la sección de simulación se ingresan:

- área del terreno
- altura del depósito
- número de orificios
- radio del orificio
- tiempo de operación

El sistema devuelve resultados como:

- presión hidrostática
- velocidad de salida
- caudal por orificio
- caudal total
- agua acumulada
- distribución por m²

### Login y administración
El sistema permite:

- iniciar sesión como administrador o campesino
- registrar campesinos
- crear terrenos
- asignar terrenos a usuarios
- controlar el estado del aspersor

---

## Consideraciones importantes

Este proyecto es una implementación de demostración académica. La lógica está diseñada para mostrar la relación entre el modelo físico y la interfaz web, sin reemplazar un sistema real de riego profesional.

---

## Autores

- Jose Miguel Bermudez Garcia
- Jhonatan Moreno Martinez
- Juan Sebastian Navarro Parra
- Maria Camila Martinez

---

## Estado del proyecto

Proyecto en desarrollo con enfoque académico y demostrativo, con funcionalidades funcionales de simulación, visualización y gestión básica del sistema.

---

## Nota

Este repositorio se encuentra organizado por capas para separar la lógica del sistema y la parte visual de la aplicación.
