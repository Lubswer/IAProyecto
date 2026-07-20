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

    # ==========================================
    # ENTRENAR MODELO DE CATEGORÍA
    # ==========================================
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
    
    # Imprimir reporte
    print("\n=== Reporte: Categoría ===")
    print(classification_report(y_test_cat, modelo_categoria.predict(X_test_cat), zero_division=0))
    
    # Guardar modelo
    joblib.dump(modelo_categoria, "modelo_categoria.pkl")
    print("    -> Modelo de categoría guardado como 'modelo_categoria.pkl'")

    # ==========================================
    # ENTRENAR MODELO DE SENTIMIENTO
    # ==========================================
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
    
    # Imprimir reporte
    print("\n=== Reporte: Sentimiento ===")
    print(classification_report(y_test_sent, modelo_sentimiento.predict(X_test_sent), zero_division=0))
    
    # Guardar modelo
    joblib.dump(modelo_sentimiento, "modelo_sentimiento.pkl")
    print("    -> Modelo de sentimiento guardado como 'modelo_sentimiento.pkl'")
    # Exportar métricas a JSON
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
