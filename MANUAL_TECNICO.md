# Manual Técnico: ConnectaNet (Análisis de Sentimientos y Categorización)

Este documento detalla los requisitos técnicos, las instrucciones de despliegue local y el funcionamiento interno de la aplicación web impulsada por Inteligencia Artificial para el análisis de texto.

---

## 1. Requisitos Previos
Para ejecutar este proyecto en tu entorno local, necesitas tener instalado lo siguiente:
*   **Python 3.9 o superior:** [Descargar Python](https://www.python.org/downloads/)
*   **Git:** Para clonar el repositorio.
*   **Un navegador web moderno:** (Chrome, Edge, Firefox, etc.) para visualizar la interfaz.

---

## 2. Instalación y Configuración

### A. Clonar el repositorio
Abre tu terminal y ejecuta el siguiente comando para descargar el código fuente:
```bash
git clone https://github.com/Lubswer/IAProyecto.git
cd IAProyecto
```

### B. Crear un Entorno Virtual (Opcional pero Recomendado)
Es buena práctica aislar las dependencias del proyecto:
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate
```

### C. Instalar Dependencias
Dirígete a la carpeta del backend e instala las librerías necesarias:
```bash
cd backend
pip install -r requirements.txt
```
*(Nota: Si no tienes el archivo `requirements.txt`, puedes instalar las librerías manualmente ejecutando: `pip install fastapi uvicorn pandas scikit-learn spacy joblib pydantic`)*

### D. Descargar el Modelo de spaCy
El proyecto requiere el modelo pre-entrenado en español de spaCy para procesar el lenguaje:
```bash
python -m spacy download es_core_news_sm
```

---

## 3. Ejecución del Proyecto

El proyecto está dividido en dos partes: el Servidor (Backend) y el Cliente (Frontend).

### Paso 1: Levantar la API (Backend)
En tu terminal, asegúrate de estar dentro de la carpeta `backend/` y ejecuta el servidor de FastAPI:
```bash
uvicorn main:app --reload
```
Verás un mensaje indicando que el servidor está corriendo en `http://127.0.0.1:8000`. 
*(Importante: No cierres esta terminal mientras uses la aplicación).*

### Paso 2: Abrir la Interfaz Web (Frontend)
No necesitas un servidor para el frontend. Simplemente:
1. Ve a la carpeta raíz del proyecto (`IA2P` / `IAProyecto`).
2. Entra a la carpeta `frontend/`.
3. Haz doble clic en el archivo **`index.html`** para que se abra en tu navegador web.

¡Listo! Ya puedes escribir un mensaje y presionar "Analizar".

---

## 4. Detalles del Dataset (Conjunto de Datos)

El modelo de inteligencia artificial se entrena a partir de un archivo llamado `nuevoDataSet.csv` ubicado en la carpeta `backend/`. Este archivo contiene ejemplos históricos para enseñar a la IA.

### Columnas del Dataset:
1.  **`texto`**: El cuerpo del mensaje original tal como lo escribió el cliente (Ej: *"El internet está muy lento hoy, arreglen esto"*).
2.  **`categoria`**: La etiqueta del departamento al que corresponde (Ej: *"Soporte Técnico"*, *"Facturación"*, *"Información"*).
3.  **`sentimiento`**: El tono emocional del mensaje (Ej: *"Positivo"*, *"Neutral"*, *"Negativo"*).

### ¿Qué se hace con estos datos?
Cuando se ejecuta el archivo `entrenador.py`, ocurre lo siguiente:
1.  **Preprocesamiento:** Se lee el CSV utilizando **Pandas**. El motor de NLP toma la columna `texto` y "limpia" las palabras. Quita los signos de puntuación y *lematiza* las palabras (por ejemplo, convierte "arreglen" en "arreglar").
2.  **Vectorización:** La máquina no entiende palabras, así que se usa `TfidfVectorizer` para convertir el texto limpio en una matriz de números basados en la frecuencia y relevancia de cada palabra.
3.  **Entrenamiento:** Se divide el dataset (75% para enseñar, 25% para evaluar).

---

## 5. Arquitectura y Modelos Usados

Si decides hacer modificaciones o entender el cerebro de la aplicación, esto es lo que ocurre internamente en `nlp_logic.py`:

*   **Clasificador de Categoría (`MultinomialNB`):** Se usa la regresión de Naive Bayes Multinomial. Es ideal para textos genéricos y clasifica el mensaje en el área correspondiente de la empresa.
*   **Clasificador de Sentimiento (`ComplementNB`):** Se usa una variante de Naive Bayes llamada "Complement". Esta es matemáticamente superior cuando el Dataset está desbalanceado (por ejemplo, cuando en el CSV hay muchas quejas negativas y muy pocas opiniones positivas).
*   **Extracción de Entidades (NER):** Antes de lematizar, el modelo de `spaCy` original lee el texto para identificar y extraer datos crudos (nombres de personas, ciudades, marcas), logrando identificar elementos clave que de otro modo pasarían desapercibidos.

Una vez que los modelos están entrenados, se exportan como archivos estáticos (`.pkl`), logrando que la API de **FastAPI** cargue instantáneamente y realice predicciones en milisegundos sin tener que re-leer el CSV original.
