# Explicación Detallada: `entrenador.py`

El archivo `entrenador.py` es el script encargado de leer el conjunto de datos (dataset), procesar los textos, entrenar los dos modelos de Inteligencia Artificial (uno para Categoría y otro para Sentimiento), y exportar tanto los modelos como sus métricas de rendimiento.

A continuación, se detalla línea por línea qué hace este código, para qué sirve cada tecnología y por qué se diseñó de esta manera.

## 1. Importación de Tecnologías y Librerías (Líneas 1 - 11)

```python
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB, ComplementNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import json

# Importar la función de lematización que construimos en la lógica
from nlp_logic import lematizar
```

*   **`pandas as pd`**: Librería esencial de análisis de datos. Sirve para cargar el archivo `.csv` como si fuera una tabla de Excel en memoria (llamada DataFrame) y manipular sus columnas fácilmente.
*   **`joblib`**: Se utiliza para la persistencia del modelo. Permite "congelar" y guardar el modelo matemático entrenado en un archivo físico (`.pkl`). Gracias a esto, la API no tiene que entrenarse desde cero cada vez que se reinicia.
*   **`sklearn` (Scikit-Learn)**: Es la librería estándar de Machine Learning en Python. De aquí extraemos:
    *   `TfidfVectorizer`: Las computadoras no entienden letras. Esta herramienta convierte el texto en una matriz de números, evaluando la frecuencia e importancia de cada palabra.
    *   `MultinomialNB` y `ComplementNB`: Los algoritmos de aprendizaje automático (Clasificadores Naive Bayes).
    *   `Pipeline`: Permite encadenar el proceso de vectorización y clasificación en un solo paso estructurado.
    *   `train_test_split`: Mezcla y divide el conjunto de datos en dos partes: una para entrenar (generalmente 75%) y otra para evaluar o examinar a la IA (25%).
    *   `classification_report`: Genera un reporte detallado con las métricas de éxito del modelo (Accuracy, Precision, Recall, F1-Score).
*   **`json`**: Librería nativa de Python para generar un archivo `.json` que el frontend pueda leer para dibujar las métricas en la web.
*   **`from nlp_logic import lematizar`**: Importa nuestra propia función que limpia y extrae las raíces de las palabras usando `spaCy`.

---

## 2. Definición de la Función y Carga de Datos (Líneas 13 - 25)

```python
def entrenar_y_guardar():
    print("[1] Iniciando proceso de entrenamiento...")
    CSV_PATH = "nuevoDataSet.csv"
    
    try:
        df = pd.read_csv(CSV_PATH)
        print(f"    -> Archivo cargado exitosamente. Filas: {len(df)}")
    except FileNotFoundError:
        print(f"\n[!] Error: No se encontró el archivo '{CSV_PATH}'.")
        return

    print("[2] Lematizando textos (esto puede tomar unos segundos)...")
    df["texto_lem"] = df["texto"].apply(lematizar)
```

*   **Líneas 13-22**: Se define la función principal. Se intenta cargar el archivo `nuevoDataSet.csv` utilizando `pd.read_csv`. Se utiliza un bloque `try-except` para que, si el archivo no existe, el programa no colapse abruptamente, sino que avise al usuario del error.
*   **Línea 25 (`df["texto_lem"] = ...`)**: Esta es una de las líneas más pesadas del código. Accede a la columna `texto` de todo el archivo CSV, y le aplica (`.apply`) a cada fila nuestra función `lematizar`. El resultado (el texto sin comas y con las palabras en su raíz) se guarda en una nueva columna llamada `texto_lem`. Esto reduce enormemente el "ruido" para la IA.

---

## 3. Entrenamiento del Modelo de Categoría (Líneas 27 - 48)

```python
    print("[3] Entrenando modelo de Categoría...")
    X_train_cat, X_test_cat, y_train_cat, y_test_cat = train_test_split(
        df["texto_lem"], df["categoria"],
        test_size=0.25, random_state=42, stratify=df["categoria"]
    )
    
    modelo_categoria = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("clf", MultinomialNB()),
    ])
    modelo_categoria.fit(X_train_cat, y_train_cat)
    
    print("\n=== Reporte: Categoría ===")
    print(classification_report(y_test_cat, modelo_categoria.predict(X_test_cat), zero_division=0))
    
    joblib.dump(modelo_categoria, "modelo_categoria.pkl")
    print("    -> Modelo de categoría guardado como 'modelo_categoria.pkl'")
```

*   **Líneas 31-34 (`train_test_split`)**: Toma los textos lematizados (`X`) y la etiqueta correcta de categoría (`y`). Reserva el 25% (`test_size=0.25`) para el examen. El parámetro `stratify=df["categoria"]` garantiza que en ese 25% de examen exista la misma proporción de categorías (Técnico, Facturación, etc.) que en el archivo total, evitando que la IA se evalúe solo con un tipo de mensaje. `random_state=42` congela la aleatoriedad para que el resultado sea siempre el mismo si lo ejecutas dos veces.
*   **Líneas 36-39 (`Pipeline`)**: Se arma la "cinta transportadora". 1) Se llama al vectorizador `TfidfVectorizer`, 2) se llama al cerebro `MultinomialNB`. Se eligió Multinomial porque es el modelo estadístico por excelencia (rápido y altamente preciso) para clasificar textos generales (categorías).
*   **Línea 40 (`.fit`)**: El momento donde la máquina "aprende". Analiza la relación matemática entre las palabras y sus categorías correspondientes basándose en el 75% de los datos de entrenamiento.
*   **Líneas 43-44 (`classification_report`)**: Le pasamos el examen (`X_test_cat`) al modelo y comparamos sus respuestas con las reales (`y_test_cat`). Imprime en consola la nota final de qué tan bien aprendió.
*   **Línea 47 (`joblib.dump`)**: Exporta el modelo entrenado (el Pipeline completo) a un archivo binario `.pkl` llamado `modelo_categoria.pkl`.

---

## 4. Entrenamiento del Modelo de Sentimiento (Líneas 50 - 71)

```python
    print("\n[4] Entrenando modelo de Sentimiento...")
    X_train_sent, X_test_sent, y_train_sent, y_test_sent = train_test_split(
        df["texto_lem"], df["sentimiento"],
        test_size=0.25, random_state=42, stratify=df["sentimiento"]
    )
    
    modelo_sentimiento = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("clf", ComplementNB()),
    ])
    modelo_sentimiento.fit(X_train_sent, y_train_sent)
    
    print("\n=== Reporte: Sentimiento ===")
    print(classification_report(y_test_sent, modelo_sentimiento.predict(X_test_sent), zero_division=0))
    
    joblib.dump(modelo_sentimiento, "modelo_sentimiento.pkl")
    print("    -> Modelo de sentimiento guardado como 'modelo_sentimiento.pkl'")
```

*   **Concepto general**: El proceso es idéntico al de categoría (Separar en Test/Train, Construir el Pipeline, Entrenar con `.fit()`, Evaluar en consola, y Guardar el `.pkl`).
*   **Diferencia Crítica (Línea 61: `ComplementNB`)**: En vez de usar `MultinomialNB`, aquí se usa `ComplementNB`. Esto se hace intencionalmente porque en problemas reales de atención al cliente, los sentimientos están inherentemente **desbalanceados** (suele haber muchísimas más quejas y reclamos que cumplidos). `ComplementNB` es un algoritmo diseñado de fábrica para corregir matemáticamente los sesgos en datasets desbalanceados, evitando que el modelo se vuelva pesimista y diga que "todo es negativo".

---

## 5. Exportación de Métricas a JSON y Cierre (Líneas 72 - 97)

```python
    print("\n[5] Exportando métricas a metricas.json...")
    reporte_cat = classification_report(y_test_cat, modelo_categoria.predict(X_test_cat), zero_division=0, output_dict=True)
    reporte_sent = classification_report(y_test_sent, modelo_sentimiento.predict(X_test_sent), zero_division=0, output_dict=True)
    
    metricas = {
        "cat_acc": reporte_cat["accuracy"],
        "cat_prec": reporte_cat["macro avg"]["precision"],
        "cat_rec": reporte_cat["macro avg"]["recall"],
        "cat_f1": reporte_cat["macro avg"]["f1-score"],
        "sent_acc": reporte_sent["accuracy"],
        "sent_prec": reporte_sent["macro avg"]["precision"],
        "sent_rec": reporte_sent["macro avg"]["recall"],
        "sent_f1": reporte_sent["macro avg"]["f1-score"],
        "total_filas": len(df)
    }
    
    with open("metricas.json", "w", encoding="utf-8") as f:
        json.dump(metricas, f, indent=4)
        
    print("\n[OK] Entrenamiento Finalizado Exitosamente.")
    print("    Ya puedes ejecutar 'uvicorn main:app --reload' para iniciar la API.")

if __name__ == "__main__":
    entrenar_y_guardar()
```

*   **Líneas 74-75**: Se vuelve a ejecutar la función de reporte (el examen final), pero esta vez pasamos el argumento `output_dict=True` para que Python no imprima el resultado como un simple texto, sino que lo convierta en un Diccionario de datos programable, para poder extraer cada variable por separado.
*   **Líneas 77-87 (`metricas`)**: Construimos nuestro propio diccionario limpio filtrando del inmenso reporte solo lo que le importa al Frontend: La exactitud (Accuracy), la precisión (Precision), la sensibilidad (Recall) y la puntuación armónica (F1-score) promediada (`macro avg`) de ambos modelos. También inyectamos el total de filas del dataset usando `len(df)`.
*   **Líneas 89-90 (`open ... json.dump`)**: Se abre (o crea) un archivo web estándar llamado `metricas.json` y se inyecta nuestro diccionario en formato JSON limpio. Esta es la técnica clave que permite que la página web (Javascript puro) lea las métricas de rendimiento y las dibuje gráficamente al instante, sin necesidad de conectarse a la Base de Datos o tener Python instalado del lado del cliente.
*   **Líneas 95-97 (`if __name__ == "__main__":`)**: Es un estándar sagrado de Python. Le indica al compilador que si el usuario abre este archivo directamente desde la consola (ejecutando `python entrenador.py`), debe arrancar automáticamente la función `entrenar_y_guardar()`. Si este archivo fuera importado desde otro lado, esa función no se dispararía sola.
