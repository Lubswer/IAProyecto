from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os

# Importar la función que hace todo el trabajo pesado usando los modelos .pkl
from nlp_logic import analizar_mensaje

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

@app.post("/analizar")
def analizar_endpoint(mensaje: Mensaje):
    # analizar_mensaje ahora devuelve un diccionario con las predicciones, confianza y entidades
    resultados = analizar_mensaje(mensaje.texto)
    return resultados

@app.get("/metricas")
def metricas_endpoint():
    """Devuelve las métricas globales del entrenamiento del modelo."""
    if os.path.exists("metricas.json"):
        with open("metricas.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"error": "Métricas no encontradas. Entrena el modelo primero."}

from fastapi.responses import PlainTextResponse
@app.get("/markdown", response_class=PlainTextResponse)
def markdown_endpoint():
    """Devuelve el contenido del archivo Markdown para la documentación."""
    path = os.path.join(os.path.dirname(__file__), "..", "Evolucion_del_Proyecto.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "Archivo no encontrado."
