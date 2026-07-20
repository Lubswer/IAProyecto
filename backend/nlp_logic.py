import spacy
import joblib
import os

# Cargar el modelo de lenguaje de spaCy
nlp = spacy.load("es_core_news_sm")

# Variables globales para no cargar los modelos en cada petición
modelo_categoria = None
modelo_sentimiento = None

def lematizar(texto):
    """Normaliza el texto: lematiza y quita puntuación."""
    doc = nlp(str(texto))
    return " ".join(token.lemma_.lower() for token in doc if not token.is_punct)

def cargar_modelos():
    """Carga los modelos entrenados desde el disco duro a la memoria."""
    global modelo_categoria, modelo_sentimiento
    
    # Asegurarse de que los modelos existan
    if not os.path.exists("modelo_categoria.pkl") or not os.path.exists("modelo_sentimiento.pkl"):
        raise FileNotFoundError("No se encontraron los archivos .pkl. Por favor, ejecuta 'python entrenador.py' primero.")

    if modelo_categoria is None:
        modelo_categoria = joblib.load("modelo_categoria.pkl")
    if modelo_sentimiento is None:
        modelo_sentimiento = joblib.load("modelo_sentimiento.pkl")

def analizar_mensaje(texto):
    """Lematiza el texto y hace la predicción usando los modelos cargados."""
    cargar_modelos()
    
    # Parsear con spaCy
    doc = nlp(str(texto))
    tokens_originales = [token.text for token in doc]
    
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
    
    # Extraer el desglose completo de sentimientos
    clases_sent = modelo_sentimiento.classes_
    desglose_sentimiento = {str(clase): round(prob * 100, 2) for clase, prob in zip(clases_sent, probs_sent)}
    
    return {
        "categoria": categoria,
        "confianza_categoria": conf_categoria,
        "sentimiento": sentimiento,
        "confianza_sentimiento": conf_sentimiento,
        "desglose_sentimiento": desglose_sentimiento,
        "nlp_debug": {
            "tokens": tokens_originales,
            "texto_lematizado": texto_lem
        }
    }
