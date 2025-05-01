from transformers import pipeline

# Initialize the zero-shot classification pipeline with the specified model
classifier = pipeline(
    "zero-shot-classification",
    model="joeddav/xlm-roberta-large-xnli",
    hypothesis_template="Bu metin {} hakkında."
)

# Define the candidate labels for classification
LABELS = [
    "platform işi deneyimi",
    "müşteri deneyimi",
    "uygulama hatası veya teknik problem",
    "genel yorum"
]

# Classify whether the given text is related to 'platform işi deneyimi'.
def classify_platform_work(text, threshold=0.4):
    # Validate input
    if not isinstance(text, str) or not text.strip():
        return False

    try:
        # Perform zero-shot classification
        result = classifier(text, candidate_labels=LABELS)
        top_label = result['labels'][0]
        top_score = result['scores'][0]

        return top_label == "platform işi deneyimi" and top_score >= threshold
    except Exception as e:
        # Handle and log any errors during classification
        print(f"❌ Classification error: {e}")
        return False