from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from classifier.training_data import TRAINING_DATA

_vectorizer = None
_model = None

def train():
    global _vectorizer, _model
    texts = [t[0] for t in TRAINING_DATA]
    labels = [t[1] for t in TRAINING_DATA]

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )

    _vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    X_train_vec = _vectorizer.fit_transform(X_train)
    X_test_vec = _vectorizer.transform(X_test)

    _model = LogisticRegression(max_iter=1000)
    _model.fit(X_train_vec, y_train)

    preds = _model.predict(X_test_vec)
    acc = accuracy_score(y_test, preds)
    report = classification_report(y_test, preds)
    return acc, report

def classify(query):
    global _vectorizer, _model
    if _model is None:
        train()
    vec = _vectorizer.transform([query])
    return _model.predict(vec)[0]
