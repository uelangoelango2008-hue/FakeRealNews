import os
import re
import pickle
import joblib
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Base directory for reliable file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "fake_news_model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "tfidf_vectorizer.pkl")

# Load model and vectorizer with graceful fallback
def load_artifact(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Required model artifact not found: {file_path}")
    try:
        return joblib.load(file_path)
    except Exception:
        with open(file_path, "rb") as f:
            return pickle.load(f)

print("[INFO] Loading Machine Learning model and TF-IDF vectorizer...")
model = load_artifact(MODEL_PATH)
vectorizer = load_artifact(VECTORIZER_PATH)
print(f"[INFO] Successfully loaded model: {type(model).__name__}")
print(f"[INFO] Successfully loaded vectorizer with {len(vectorizer.vocabulary_)} features")


def clean_text(text: str) -> str:
    """
    Preprocess text to normalize input matching the training pipeline:
    - Lowercase conversion
    - Remove URLs and hyperlinks
    - Replace special characters / punctuation with space
    - Collapse redundant whitespace
    """
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def predict_news(raw_text: str):
    """
    Core prediction pipeline:
    - Input validation
    - Text cleaning
    - TF-IDF vector transformation
    - Logistic Regression classification
    - Confidence score extraction via class probabilities
    """
    if not raw_text or not raw_text.strip():
        return None, "Please enter some news text to analyze."

    cleaned = clean_text(raw_text)
    if not cleaned:
        return None, "The provided text contains only invalid characters or symbols. Please enter valid news content."

    # Transform text to TF-IDF features
    features = vectorizer.transform([cleaned])

    # Class probabilities [P(Fake=0), P(Real=1)]
    probabilities = model.predict_proba(features)[0]
    pred_class = int(model.predict(features)[0])

    # Class 0 = Fake News, Class 1 = Real News (as per WELFake benchmark)
    if pred_class == 1:
        label = "Real News"
        badge = "Real News ✅"
        status = "real"
        confidence = float(probabilities[1]) * 100.0
    else:
        label = "Fake News"
        badge = "Fake News ❌"
        status = "fake"
        confidence = float(probabilities[0]) * 100.0

    # Categorize confidence tier
    if confidence >= 85.0:
        confidence_tier = "High Confidence"
    elif confidence >= 65.0:
        confidence_tier = "Medium Confidence"
    else:
        confidence_tier = "Low Confidence"

    words = len(raw_text.split())
    chars = len(raw_text)
    clean_tokens = cleaned.split()
    unique_words = len(set(clean_tokens))
    lexical_diversity = round((unique_words / max(1, len(clean_tokens))) * 100, 1) if clean_tokens else 0.0
    reading_time = max(1, round(words / 200)) if words > 100 else 1
    
    # Assess sensationalism markers
    exclamation_count = raw_text.count("!")
    caps_count = sum(1 for w in raw_text.split() if w.isupper() and len(w) > 2)
    if exclamation_count >= 2 or caps_count >= 3:
        tone_indicator = "Sensational / Emotional Markers Detected"
    else:
        tone_indicator = "Standard / Objective Linguistic Style"

    result = {
        "raw_text": raw_text,
        "cleaned_text": cleaned,
        "prediction": badge,
        "label": label,
        "status": status,
        "pred_class": pred_class,
        "confidence": round(confidence, 2),
        "confidence_tier": confidence_tier,
        "fake_probability": round(float(probabilities[0]) * 100.0, 2),
        "real_probability": round(float(probabilities[1]) * 100.0, 2),
        "word_count": words,
        "char_count": chars,
        "unique_words": unique_words,
        "lexical_diversity": lexical_diversity,
        "reading_time": reading_time,
        "tone_indicator": tone_indicator,
    }
    return result, None


@app.route("/", methods=["GET", "POST"])
@app.route("/predict", methods=["POST"])
def home():
    result = None
    validation_error = None
    news_input = ""

    if request.method == "POST":
        news_input = request.form.get("news", "")
        result, validation_error = predict_news(news_input)

    return render_template(
        "index.html",
        result=result,
        validation_error=validation_error,
        news_input=news_input,
    )


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """REST API endpoint for programmatic inference and automated testing."""
    if not request.is_json:
        return jsonify({"status": "error", "message": "Expected JSON payload with 'news' key"}), 400

    data = request.get_json()
    news_text = data.get("news", "")
    result, error = predict_news(news_text)

    if error:
        return jsonify({"status": "error", "message": error}), 400

    return jsonify({"status": "success", "data": result}), 200


if __name__ == "__main__":
    # Development server
    app.run(host="0.0.0.0", port=5000, debug=True)