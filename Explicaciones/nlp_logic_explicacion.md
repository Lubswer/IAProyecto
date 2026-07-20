# Explicación Detallada: `nlp_logic.py`

El archivo `nlp_logic.py` es el verdadero **Cerebro** de la aplicación en producción. Mientras que `entrenador.py` solo se ejecuta una vez para crear los modelos, `nlp_logic.py` se ejecuta constantemente cada vez que un usuario escribe un mensaje en la web.

Su trabajo es tomar un texto en lenguaje humano (crudo), limpiarlo, cargarlo en los modelos matemáticos que ya están entrenados y devolver un veredicto.

A continuación, se detalla línea por línea:

## 1. Importaciones y Configuración Inicial (Líneas 1 - 10)

```python
import spacy
import joblib
import os

# Cargar el modelo de lenguaje de spaCy
nlp = spacy.load("es_core_news_sm")

# Variables globales para no cargar los modelos en cada petición
modelo_categoria = None
modelo_sentimiento = None
```

*   **`spacy`**: La librería líder en la industria para Procesamiento de Lenguaje Natural avanzado.
*   **`joblib`**: Se utiliza aquí no para guardar, sino para **abrir** (cargar) los modelos que `entrenador.py` congeló previamente.
*   **`os`**: Librería del sistema operativo. Nos sirve para verificar si los archivos `.pkl` existen físicamente en la carpeta antes de intentar abrirlos y que el programa colapse.
*   **`nlp = spacy.load(...)`**: Carga el modelo `es_core_news_sm`, que es un diccionario/red neuronal pre-entrenada por la comunidad para entender el idioma español (verbos, sustantivos, gramática).
*   **`modelo_categoria = None` (Variables Globales)**: **Este es un truco de rendimiento web fundamental.** Si cargáramos los archivos del disco duro cada vez que alguien envía un texto, la página web sería muy lenta. Al declararlas globales, las cargaremos a la Memoria RAM una sola vez y las re-usaremos miles de veces a la velocidad de la luz.

---

## 2. La Función de Limpieza: Lematización (Líneas 12 - 15)

```python
def lematizar(texto):
    """Normaliza el texto: lematiza y quita puntuación."""
    doc = nlp(str(texto))
    return " ".join(token.lemma_.lower() for token in doc if not token.is_punct)
```

*   **¿Qué hace?**: Recibe un texto crudo ("Los servicios fallaron!") y se lo pasa a spaCy (`nlp(str(texto))`).
*   **El Filtro**: Usa una comprensión de listas en Python. Por cada palabra (`token`), revisa que NO sea puntuación (`not token.is_punct`). Si es una palabra válida, extrae su forma base matemática (`lemma_`) y la pasa a minúscula (`lower()`). Finalmente, vuelve a unir todo en una sola frase con espacios (`" ".join(...)`).
*   **Ejemplo**: "Los servicios fallaron!" -> "el servicio fallar". Esto facilita enormemente el trabajo de la Inteligencia Artificial porque ya no tiene que aprender que "falló", "fallaron" y "fallan" son lo mismo; todas se convierten en "fallar".

---

## 3. Carga en Memoria (Caché) (Líneas 17 - 28)

```python
def cargar_modelos():
    """Carga los modelos entrenados desde el disco duro a la memoria."""
    global modelo_categoria, modelo_sentimiento
    
    if not os.path.exists("modelo_categoria.pkl") or not os.path.exists("modelo_sentimiento.pkl"):
        raise FileNotFoundError("No se encontraron los archivos .pkl. Por favor, ejecuta 'python entrenador.py' primero.")

    if modelo_categoria is None:
        modelo_categoria = joblib.load("modelo_categoria.pkl")
    if modelo_sentimiento is None:
        modelo_sentimiento = joblib.load("modelo_sentimiento.pkl")
```

*   **Línea 19 (`global`)**: Le dice a Python que vamos a usar y modificar las variables globales que declaramos arriba.
*   **Línea 21-23**: Verifica físicamente si los archivos `.pkl` existen (`os.path.exists`). Si alguien intenta encender la API sin haber corrido el entrenador antes, detiene todo y lanza un error amigable.
*   **Líneas 25-28 (`is None`)**: Patrón de diseño "Singleton / Lazy Loading". Solo lee el disco duro (`joblib.load`) si los modelos están vacíos (`None`). Si el modelo ya está cargado en la RAM, se salta este paso al instante.

---

## 4. El Corazón Analítico: Procesar Mensaje (Líneas 30 - 64)

```python
def analizar_mensaje(texto):
    cargar_modelos()
    
    # 1. Extraer entidades usando spaCy original (sin lematizar)
    doc = nlp(str(texto))
    entidades = [{"texto": ent.text, "etiqueta": ent.label_} for ent in doc.ents]
    
    # 2. Lematizar usando el doc ya parseado
    texto_lem = " ".join(token.lemma_.lower() for token in doc if not token.is_punct)
    
    # 3. Predicciones
    categoria = modelo_categoria.predict([texto_lem])[0]
    sentimiento = modelo_sentimiento.predict([texto_lem])[0]
    
    # 4. Confianza (Porcentaje)
    probs_cat = modelo_categoria.predict_proba([texto_lem])[0]
    conf_categoria = round(max(probs_cat) * 100, 2)
    
    probs_sent = modelo_sentimiento.predict_proba([texto_lem])[0]
    conf_sentimiento = round(max(probs_sent) * 100, 2)
    
    clases_sent = modelo_sentimiento.classes_
    desglose_sentimiento = {str(clase): round(prob * 100, 2) for clase, prob in zip(clases_sent, probs_sent)}
    
    return {
        "categoria": categoria,
        "confianza_categoria": conf_categoria,
        "sentimiento": sentimiento,
        "confianza_sentimiento": conf_sentimiento,
        "desglose_sentimiento": desglose_sentimiento,
        "entidades": entidades
    }
```

*   **Líneas 35-36 (Extracción de Entidades - NER)**: Antes de arruinar el texto original lematizándolo, se lo pasamos a spaCy. spaCy es capaz de reconocer mágicamente sustantivos propios (como "México" que es un `LOC` o Localidad, o "Juan" que es `PER` Persona). Extraemos esto y lo guardamos en un arreglo.
*   **Líneas 38-39**: Ahora sí, lematizamos la oración limpia.
*   **Líneas 41-43 (`.predict`)**: Le preguntamos a la Inteligencia Artificial (a los archivos `.pkl`) que predigan a qué categoría pertenece el texto y qué sentimiento tiene.
*   **Líneas 45-50 (`predict_proba`)**: Esto es ingeniería avanzada. En lugar de pedirle a la máquina "qué decidió", le pedimos la "Probabilidad Matemática" detrás de su decisión (`predict_proba`). Extraemos la probabilidad máxima (`max`), la multiplicamos por 100 para hacerla un porcentaje, y la redondeamos a 2 decimales para que el Frontend dibuje la barra de progreso.
*   **Líneas 52-54 (`desglose_sentimiento`)**: Hacemos un cierre o emparejamiento (`zip`) entre los nombres de las clases (Negativo, Positivo) y sus respectivas probabilidades. Esto es lo que permite que el frontend dibuje tres barras indicadoras separadas y el usuario vea cómo está "pensando" la IA.
*   **Líneas 56-64 (`return { ... }`)**: Toda esta gigantesca operación matemática se empaqueta limpia y ordenadamente en un Diccionario de Python (que es nativamente convertible a JSON), y se lo entrega a la API (FastAPI) para que lo lance por internet.
