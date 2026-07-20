# Explicación Detallada: `main.py`

El archivo `main.py` es la **API (Interfaz de Programación de Aplicaciones)** del proyecto. Actúa como el portero o recepcionista. Su trabajo no es analizar texto matemáticamente (para eso está `nlp_logic.py`), sino abrir "rutas web" en el servidor, escuchar las peticiones de los navegadores por internet, enviarle los datos al cerebro y devolver las respuestas.

A continuación, se detalla línea por línea:

## 1. Importación de Tecnologías Web (Líneas 1 - 9)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os

# Importar la función que hace todo el trabajo pesado usando los modelos .pkl
from nlp_logic import analizar_mensaje
```

*   **`FastAPI`**: Es un framework web moderno y ultra rápido para Python. Reemplaza a Flask o Django, y está diseñado específicamente para crear APIs de Inteligencia Artificial de forma masiva.
*   **`CORSMiddleware`**: CORS es una medida de seguridad de los navegadores. Si un frontend en el puerto 5500 intenta pedirle datos a un backend en el puerto 8000, el navegador lo bloquea asumiendo que es un hackeo. El `CORSMiddleware` desactiva este escudo permitiendo que ambos se hablen amistosamente.
*   **`BaseModel (Pydantic)`**: Pydantic es una librería que obliga a que los datos tengan tipos estrictos (string, int). Es el escudo de seguridad de la API contra inyecciones malas de código.
*   **`json` y `os`**: Librerías nativas para leer archivos del disco duro (como el `metricas.json` o el Markdown).
*   **`from nlp_logic import analizar_mensaje`**: Importamos la función maestra que construimos en el archivo cerebral.

---

## 2. Configuración del Servidor y Seguridad (Líneas 10 - 23)

```python
app = FastAPI(title="API de Análisis de Sentimiento y Categoría")

# Configurar CORS para permitir que cualquier frontend (React, HTML, etc) se conecte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definir la estructura de datos esperada del Frontend
class Mensaje(BaseModel):
    texto: str
```

*   **Línea 10 (`app = FastAPI(...)`)**: Instanciamos el servidor web.
*   **Líneas 12-19 (`app.add_middleware`)**: Insertamos el permiso CORS. `allow_origins=["*"]` significa "Permitir que *CUALQUIER* página web del universo se conecte y pida análisis a mi IA". En un entorno bancario real, esto se restringiría únicamente a `["https://mipagina.com"]`.
*   **Líneas 21-23 (`class Mensaje(BaseModel)`)**: Declaramos cómo tiene que verse el paquete de datos que envíe la página web. Exigimos que llegue estrictamente con una llave llamada `texto` y que el contenido sea exclusivamente una cadena de texto (`str`). Si el frontend nos enviara un número o una imagen, FastAPI lo rechazaría automáticamente gracias a esta regla.

---

## 3. El Endpoint Principal: Análisis (Líneas 25 - 29)

```python
@app.post("/analizar")
def analizar_endpoint(mensaje: Mensaje):
    # analizar_mensaje ahora devuelve un diccionario con las predicciones, confianza y entidades
    resultados = analizar_mensaje(mensaje.texto)
    return resultados
```

*   **Línea 25 (`@app.post("/analizar")`)**: Esto es un decorador de enrutamiento. Le dice al servidor: "Si alguien navega o envía datos a `http://localhost:8000/analizar` usando el método POST (envío oculto de datos), ejecuta la función de abajo".
*   **Línea 26 (`mensaje: Mensaje`)**: Exige que el cuerpo de la petición cumpla con el escudo que creamos arriba.
*   **Línea 28 (`analizar_mensaje(...)`)**: Extrae el texto que el usuario escribió en la interfaz gráfica (`mensaje.texto`), y se lo inyecta a nuestra función maestra del `nlp_logic.py`.
*   **Línea 29 (`return resultados`)**: Automáticamente agarra el diccionario de Python que devolvió el cerebro y lo transforma a un `.json` perfecto para ser arrojado a través de internet de vuelta hacia `app.js`.

---

## 4. El Endpoint de Métricas Estáticas (Líneas 31 - 37)

```python
@app.get("/metricas")
def metricas_endpoint():
    """Devuelve las métricas globales del entrenamiento del modelo."""
    if os.path.exists("metricas.json"):
        with open("metricas.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"error": "Métricas no encontradas. Entrena el modelo primero."}
```

*   **Línea 31 (`@app.get("/metricas")`)**: Expone una ruta GET (de solo lectura). El Frontend (`app.js`) hace un `fetch` a esta ruta apenas se carga la página para saber qué tan inteligente es la IA.
*   **Líneas 34-36**: Utiliza `os.path.exists` para evitar errores. Abre el archivo `metricas.json` que generó el `entrenador.py` en modo lectura (`"r"`) y lo expulsa directamente al navegador usando `json.load`. 

---

## 5. El Endpoint del Motor Documental (Líneas 39 - 47)

```python
from fastapi.responses import PlainTextResponse
@app.get("/markdown", response_class=PlainTextResponse)
def markdown_endpoint():
    """Devuelve el contenido del archivo Markdown para la documentación."""
    path = os.path.join(os.path.dirname(__file__), "..", "Evolucion_del_Proyecto.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "Archivo no encontrado."
```

*   **Línea 39 (`PlainTextResponse`)**: Un navegador web generalmente asume que todo lo que le manda FastAPI es JSON. Aquí importamos un comando para decirle explícitamente a la web: *"Te voy a mandar un documento de texto puro gigante, no te asustes"*.
*   **Línea 40 (`@app.get("/markdown")`)**: Habilitamos otra ruta de lectura en el puerto 8000.
*   **Línea 43 (`os.path.join(...)`)**: Truco avanzado de ingeniería. Ya que `Evolucion_del_Proyecto.md` no está adentro de la carpeta `/backend/`, sino una carpeta más arriba (en la carpeta madre), usamos `..` (volver atrás) para obligar al servidor a salir de su caja fuerte, entrar a la carpeta principal, buscar el `.md` y leerlo (`f.read()`). Todo esto se le envía al frontend para que la librería `marked.js` lo dibuje con colores mágicos.
