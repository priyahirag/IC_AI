"""
nlp_classifier.py
=================

The AI/NLP part of CrisisLens: it reads a free-text disaster report and
predicts three things.

    Report text  ->  TF-IDF  ->  Logistic Regression  ->  Disaster Type
                                                          Severity
                                                          Resource Need

HOW IT IS BUILT
---------------
Three independent scikit-learn models, one per label:

    models/disaster_classifier.pkl   +  models/disaster_vectorizer.pkl
    models/severity_classifier.pkl   +  models/severity_vectorizer.pkl
    models/resource_classifier.pkl   +  models/resource_vectorizer.pkl

Each pair is a TF-IDF vectorizer feeding a Logistic Regression classifier.
No deep learning, no external APIs, everything runs offline.

USAGE
-----
Train (creates the six .pkl files and prints prototype accuracy):
    python src/nlp_classifier.py

Predict from another module:
    from nlp_classifier import analyze_report
    analyze_report("Heavy rainfall has flooded several houses.")

IMPORTANT NOTE ON ACCURACY
--------------------------
The numbers printed by train_models() are prototype accuracy measured on a
small SYNTHETIC dataset written for this hackathon. They are NOT validated
real-world emergency-response accuracy and must not be presented as such.
"""

from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# This file lives in src/, so the project root is one folder up.
try:  # imported as part of the src package
    from .data_ingestion import load_reports
except ImportError:  # run directly, e.g. "python src/nlp_classifier.py"
    from data_ingestion import load_reports

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "models"

# Fixed seed everywhere so every run gives the same numbers.
RANDOM_STATE = 42
TEST_SIZE = 0.25

# The three models we build. Keeping this in one place means train_models()
# and analyze_report() can never drift apart.
CLASSIFIERS = [
    {
        "name": "disaster",
        "label_column": "disaster_type",
        "display_name": "Disaster Type",
    },
    {
        "name": "severity",
        "label_column": "severity",
        "display_name": "Severity",
    },
    {
        "name": "resource",
        "label_column": "resource_need",
        "display_name": "Resource Need",
    },
]

# Simple in-memory cache so we do not re-read the .pkl files on every single
# call to analyze_report(). Keyed by classifier name.
_MODEL_CACHE = {}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def _model_paths(name):
    """Return (classifier_path, vectorizer_path) for a model name."""
    classifier_path = MODELS_DIR / f"{name}_classifier.pkl"
    vectorizer_path = MODELS_DIR / f"{name}_vectorizer.pkl"
    return classifier_path, vectorizer_path


def _make_vectorizer():
    """Create a fresh TF-IDF vectorizer.

    - lowercase   : "Flood" and "flood" become the same feature
    - stop_words  : drops very common English words like "the", "is"
    - ngram_range : looks at single words AND two-word phrases, so phrases
                    like "heavy rainfall" or "gas leak" count as one feature
    """
    return TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
    )


def _make_classifier():
    """Create a fresh Logistic Regression classifier."""
    return LogisticRegression(
        max_iter=1000,
        random_state=RANDOM_STATE,
    )


def _split(texts, labels):
    """Split into train/test sets, keeping the label mix balanced if possible.

    With a small dataset a rare label can end up with only one example, and
    stratifying would then fail. In that case we quietly fall back to a plain
    random split so the training script still runs.
    """
    try:
        return train_test_split(
            texts,
            labels,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            stratify=labels,
        )
    except ValueError:
        print(
            "  (A label has too few examples to stratify; "
            "using a plain random split instead.)"
        )
        return train_test_split(
            texts,
            labels,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
        )


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------
def train_models():
    """
    Train all three classifiers and save six .pkl files.

    Steps:
      1. Load the dataset.
      2. Split into training and testing sets.
      3. Build a TF-IDF vectorizer and a Logistic Regression for each label.
      4. Save the fitted vectorizer and model to models/.
      5. Print prototype accuracy for each classifier.

    Returns
    -------
    dict
        {"disaster": <accuracy>, "severity": <accuracy>, "resource": <accuracy>}
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("CrisisLens - training NLP classifiers")
    print("=" * 60)

    # --- 1. Load the data -------------------------------------------------
    reports = load_reports()
    texts = reports["report_text"]
    print(f"Loaded {len(reports)} reports from data/raw/disaster_reports.csv")
    print(f"Train/test split: {int((1 - TEST_SIZE) * 100)}% / {int(TEST_SIZE * 100)}%")
    print()

    accuracies = {}

    # --- 2./3./4. One model per label ------------------------------------
    for config in CLASSIFIERS:
        name = config["name"]
        label_column = config["label_column"]
        display_name = config["display_name"]

        print(f"--- {display_name} classifier ---")

        labels = reports[label_column]

        X_train, X_test, y_train, y_test = _split(texts, labels)

        # Turn the raw text into numbers the model can use. The vectorizer is
        # fitted ONLY on the training text, then reused on the test text.
        vectorizer = _make_vectorizer()
        X_train_features = vectorizer.fit_transform(X_train)
        X_test_features = vectorizer.transform(X_test)

        # Learn the mapping from those numbers to the labels.
        classifier = _make_classifier()
        classifier.fit(X_train_features, y_train)

        # How well did it do on the held-out test rows?
        predictions = classifier.predict(X_test_features)
        accuracies[name] = accuracy_score(y_test, predictions)

        # --- 5. Save both pieces -----------------------------------------
        # We must save the vectorizer too: at prediction time the text has to
        # be converted into the exact same features the model was trained on.
        classifier_path, vectorizer_path = _model_paths(name)
        joblib.dump(classifier, classifier_path)
        joblib.dump(vectorizer, vectorizer_path)

        print(f"  Saved: models/{classifier_path.name}")
        print(f"  Saved: models/{vectorizer_path.name}")
        print()

    # --- 6. Prototype accuracy -------------------------------------------
    print("=" * 60)
    print("PROTOTYPE ACCURACY (synthetic dataset - not real-world accuracy)")
    print("=" * 60)
    for config in CLASSIFIERS:
        name = config["name"]
        print(f"{config['display_name']} Accuracy: {accuracies[name]:.2f}")
    print()
    print("Reminder: these numbers come from ~100 hand-written synthetic")
    print("reports. Real emergency reporting is far more varied. Treat these")
    print("as a sanity check that the pipeline works, nothing more.")
    print("=" * 60)

    return accuracies


# ---------------------------------------------------------------------------
# Loading saved models
# ---------------------------------------------------------------------------
def _load_bundle(name):
    """Load (classifier, vectorizer) for one model name, with caching."""
    if name in _MODEL_CACHE:
        return _MODEL_CACHE[name]

    classifier_path, vectorizer_path = _model_paths(name)

    if not classifier_path.exists() or not vectorizer_path.exists():
        raise FileNotFoundError(
            f"Model files for '{name}' were not found in {MODELS_DIR}.\n"
            "Train them first with:  python src/nlp_classifier.py"
        )

    bundle = (joblib.load(classifier_path), joblib.load(vectorizer_path))
    _MODEL_CACHE[name] = bundle
    return bundle


def ensure_models_trained():
    """If any .pkl file is missing, train everything from scratch."""
    missing = []
    for config in CLASSIFIERS:
        for path in _model_paths(config["name"]):
            if not path.exists():
                missing.append(path.name)

    if missing:
        print("[nlp_classifier] Missing model file(s): "
              f"{', '.join(missing)}")
        print("[nlp_classifier] Training them now - this takes a few seconds.")
        train_models()


# ---------------------------------------------------------------------------
# The function the rest of the pipeline uses
# ---------------------------------------------------------------------------
def analyze_report(text):
    """
    Run a raw disaster report through all three trained models.

    Parameters
    ----------
    text : str
        The free-text report, e.g. "Water entered homes and two people are
        stranded."

    Returns
    -------
    dict
        {
            "disaster_type": "Flood",
            "severity": "High",
            "resource_need": "Rescue"
        }
    """
    if text is None or not str(text).strip():
        raise ValueError("analyze_report() needs a non-empty report text.")

    # Train on the fly if the models have not been built yet, so a teammate
    # who forgets to run training still gets a working pipeline.
    ensure_models_trained()

    cleaned_text = str(text).strip()

    result = {}
    for config in CLASSIFIERS:
        classifier, vectorizer = _load_bundle(config["name"])

        # Same two steps as training: text -> numbers -> prediction.
        features = vectorizer.transform([cleaned_text])
        prediction = classifier.predict(features)[0]

        # str() keeps the output JSON-friendly (numpy types are not).
        result[config["label_column"]] = str(prediction)

    return {
        "disaster_type": result["disaster_type"],
        "severity": result["severity"],
        "resource_need": result["resource_need"],
    }


# ---------------------------------------------------------------------------
# Run this file directly to train:  python src/nlp_classifier.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    train_models()
