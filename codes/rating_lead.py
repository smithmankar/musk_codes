# --- Install dependencies if not already done ---
# pip install pandas scikit-learn transformers torch

import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline as hf_pipeline

# --- 1️⃣ Load Data ---
training_file = "training.csv"
to_reclassify_file = "to_reclassify.csv"

training_df = pd.read_csv(training_file)
to_reclassify_df = pd.read_csv(to_reclassify_file)

X_train = training_df['Why do you wanna do this internship?'].astype(str)
y_train_raw = training_df['Quality']

# ✅ Drop rows with missing labels
mask = y_train_raw.notna()
X_train = X_train[mask]
y_train = y_train_raw[mask].astype(str)

print(f"✅ Loaded training data: {len(X_train)} samples after dropping empty labels.")

X_test = to_reclassify_df['Reason'].astype(str)

# --- 2️⃣ Train Logistic Regression Classifier ---
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words='english',
        max_df=0.9,
        min_df=2
    )),
    ('clf', LogisticRegression(max_iter=1000, solver='lbfgs'))
])

# Cross-validation (skip if too small)
try:
    scores = cross_val_score(pipeline, X_train, y_train, cv=2, scoring='accuracy')
    print(f"✅ Cross-validation Accuracy: {scores.mean():.3f} (+/- {scores.std():.3f})")
except ValueError as e:
    print(f"⚠️ Cross-validation skipped: {e}")

# Train final model
pipeline.fit(X_train, y_train)

# Predict
predicted_quality = pipeline.predict(X_test)
predicted_probs = pipeline.predict_proba(X_test)

# --- 3️⃣ Safe Flexible Profanity Detection ---
base_curse_words = [
    "fuck", "shit", "bitch", "bastard", "asshole",
    "chutiya", "madarchod", "behenchod", "bhenchod",
    "lund", "gaand", "saala", "randi", "bc", "mc"
]

flexible_patterns = []
for word in base_curse_words:
    pattern = r'\b'
    for letter in word:
        pattern += re.escape(letter) + r'[\W_]*'
    pattern = pattern.rstrip(r'[\W_]*')
    pattern += r'\b'
    flexible_patterns.append(pattern)

flexible_curse_pattern = re.compile(r'(' + '|'.join(flexible_patterns) + r')', re.IGNORECASE)

def check_profanity(text):
    return bool(flexible_curse_pattern.search(text))

profanity_flags = X_test.apply(check_profanity)

# --- 4️⃣ AI Toxicity Detection ---
MODEL_NAME = "unitary/toxic-bert"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

toxicity_pipeline = hf_pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    device=-1,
    batch_size=8
)

toxicity_results = toxicity_pipeline(
    list(X_test),
    truncation=True  # 🚩 prevents 512 token errors
)

tox_labels = [r['label'] for r in toxicity_results]
tox_scores = [r['score'] for r in toxicity_results]

to_reclassify_df['AI_Toxic_Label'] = tox_labels
to_reclassify_df['AI_Toxic_Score'] = tox_scores

# --- 5️⃣ Combine All Checks for Final Label ---
final_labels = []
for predicted, is_profanity, tox_label, tox_score in zip(
    predicted_quality, profanity_flags, tox_labels, tox_scores
):
    if is_profanity:
        final_labels.append("Bad")
    elif tox_label.lower() == 'toxic' and tox_score > 0.6:
        final_labels.append("Bad")
    else:
        final_labels.append(predicted)

# --- 6️⃣ Save Results ---
to_reclassify_df['Predicted_Quality'] = final_labels
to_reclassify_df['Profanity_Found'] = profanity_flags

# Add classifier probabilities
class_labels = pipeline.classes_
for idx, label in enumerate(class_labels):
    to_reclassify_df[f'Prob_{label}'] = predicted_probs[:, idx]

output_file = "reclassified_leads_combined_final.csv"
to_reclassify_df.to_csv(output_file, index=False)

print(f"✅ Done! Results saved as '{output_file}'")
