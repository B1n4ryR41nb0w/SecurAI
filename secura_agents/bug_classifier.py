import pandas as pd
import torch
from pathlib import Path
import os
from transformers import RobertaTokenizer, RobertaForSequenceClassification
from transformers import Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import pickle


project_root = Path(os.path.dirname(os.path.abspath(__file__))).parent
DATA_PATH = project_root / "data" / "classifier_data.csv"
MODEL_OUTPUT_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "models" / "distilroberta_bug_classifier"
LABEL_ENCODER_PATH = MODEL_OUTPUT_DIR / "label_encoder.pkl"


MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Create a custom dataset class
class VulnerabilityDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


def compute_metrics(pred):
    """Compute evaluation metrics for the model."""
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }


def prepare_dataset():
    """Load and preprocess the dataset for fine-tuning."""
    try:
        df = pd.read_csv(DATA_PATH)
        print(f"✅ Dataset loaded from {DATA_PATH}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}. Please ensure classifier_data.csv exists.")

    # Enhance features by combining SWC-ID, Title, and Description
    df['combined_text'] = df.apply(
        lambda row: f"SWC-ID: {row['SWC_ID']} | Title: {row['Title']} | {row['Description']}",
        axis=1
    )

    # Map severity to integer labels
    severity_mapping = {"Low": 0, "Medium": 1, "High": 2}
    df['label'] = df['Severity'].map(severity_mapping)

    # Save the label mapping for inference
    with open(LABEL_ENCODER_PATH, 'wb') as f:
        pickle.dump(severity_mapping, f)

    # Split the dataset
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df['combined_text'].tolist(),
        df['label'].tolist(),
        test_size=0.2,
        stratify=df['label'],
        random_state=42
    )

    # Load tokenizer
    tokenizer = RobertaTokenizer.from_pretrained("distilroberta-base")

    # Tokenize data
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=256)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=256)

    # Create datasets
    train_dataset = VulnerabilityDataset(train_encodings, train_labels)
    val_dataset = VulnerabilityDataset(val_encodings, val_labels)

    # Save tokenizer for later use
    tokenizer.save_pretrained(MODEL_OUTPUT_DIR)

    return train_dataset, val_dataset


def fine_tune_model():
    """Fine-tune DistilRoBERTa on the dataset."""
    # Load model with correct number of labels
    model = RobertaForSequenceClassification.from_pretrained(
        "distilroberta-base",
        num_labels=3,
        problem_type="single_label_classification"
    )

    # Prepare datasets
    train_dataset, val_dataset = prepare_dataset()

    # Define training arguments
    training_args = TrainingArguments(
        output_dir=MODEL_OUTPUT_DIR / "checkpoints",
        num_train_epochs=3,  # Reduced for faster training
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir=MODEL_OUTPUT_DIR / "logs",
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
    )

    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )

    # Train the model
    print("🏋️ Starting model training...")
    trainer.train()

    # Evaluate the model
    eval_result = trainer.evaluate()
    print(f"📊 Evaluation results: {eval_result}")

    # Save the fine-tuned model
    model.save_pretrained(MODEL_OUTPUT_DIR)
    print(f"✅ Model fine-tuned and saved to {MODEL_OUTPUT_DIR}")


def classify_vulnerability(description, swc_id=None, title=None):
    """
    Classify a vulnerability's severity based on its description.

    Args:
        description (str): The vulnerability description
        swc_id (str, optional): The SWC ID if available
        title (str, optional): The vulnerability title if available

    Returns:
        dict: The classification result with severity and confidence
    """
    try:

        if not (MODEL_OUTPUT_DIR / "pytorch_model.bin").exists() and not (
                MODEL_OUTPUT_DIR / "model.safetensors").exists():
            print("🏋️ No trained model found. Training model on first use...")
            fine_tune_model()

        # Load the saved model and tokenizer
        model = RobertaForSequenceClassification.from_pretrained(MODEL_OUTPUT_DIR)
        tokenizer = RobertaTokenizer.from_pretrained(MODEL_OUTPUT_DIR)

        # Load the label encoder
        with open(LABEL_ENCODER_PATH, 'rb') as f:
            severity_mapping = pickle.load(f)

        # Invert the mapping for prediction
        inv_severity_mapping = {v: k for k, v in severity_mapping.items()}

        # Prepare the input text
        combined_text = f"SWC-ID: {swc_id if swc_id else 'Unknown'} | "
        combined_text += f"Title: {title if title else 'Unknown'} | {description}"

        # Tokenize the input
        inputs = tokenizer(combined_text, return_tensors="pt", truncation=True, padding=True, max_length=256)

        # Get model prediction
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            predicted_class = torch.argmax(logits, dim=1).item()

            # Get confidence scores using softmax
            probs = torch.nn.functional.softmax(logits, dim=1)[0]
            confidence = probs[predicted_class].item()

        # Map the predicted class back to severity
        severity = inv_severity_mapping[predicted_class]

        # Return the classification with confidence
        result = {
            "severity": severity,
            "confidence": float(confidence),
            "all_probabilities": {
                inv_severity_mapping[i]: float(prob) for i, prob in enumerate(probs)
            }
        }

        return result

    except Exception as e:
        print(f"Error in classify_vulnerability: {e}")
        # Fallback with rule-based classification
        description_lower = description.lower()
        title_lower = (title or "").lower()

        # Rule-based fallback
        if any(word in description_lower or word in title_lower for word in
               ['reentrancy', 'recursive', 'external call']):
            return {"severity": "High", "confidence": 0.8,
                    "all_probabilities": {"Low": 0.1, "Medium": 0.1, "High": 0.8}}
        elif any(word in description_lower or word in title_lower for word in
                 ['overflow', 'underflow', 'selfdestruct', 'suicide']):
            return {"severity": "High", "confidence": 0.9,
                    "all_probabilities": {"Low": 0.05, "Medium": 0.05, "High": 0.9}}
        elif any(word in description_lower or word in title_lower for word in
                 ['unchecked', 'return', 'failed call', 'dos']):
            return {"severity": "Medium", "confidence": 0.7,
                    "all_probabilities": {"Low": 0.2, "Medium": 0.6, "High": 0.2}}
        elif any(word in description_lower or word in title_lower for word in
                 ['pragma', 'compiler', 'deprecated', 'warning']):
            return {"severity": "Low", "confidence": 0.8, "all_probabilities": {"Low": 0.7, "Medium": 0.2, "High": 0.1}}
        else:
            return {"severity": "Medium", "confidence": 0.5,
                    "all_probabilities": {"Low": 0.3, "Medium": 0.4, "High": 0.3}}


if __name__ == "__main__":
    print(f"📂 Looking for dataset at: {DATA_PATH}")
    print(f"📂 Model will be saved to: {MODEL_OUTPUT_DIR}")

    # Check if model exists, if not train it
    if not (MODEL_OUTPUT_DIR / "pytorch_model.bin").exists() and not (MODEL_OUTPUT_DIR / "model.safetensors").exists():
        print("🏋️ No trained model found. Training new model...")
        try:
            fine_tune_model()
            print("✅ Model training completed!")
        except Exception as e:
            print(f"❌ Training failed: {e}")
            print("📝 Make sure you have classifier_data.csv with enough data")
    else:
        print("✅ Trained model already exists")

    # Test the classifier
    test_description = "The contract uses transfer() with a hardcoded gas value which may fail."
    result = classify_vulnerability(
        test_description,
        swc_id="SWC-134",
        title="Message call with hardcoded gas amount"
    )
    print("\n🧪 Test Classification Result:")
    print(f"Severity: {result['severity']} (Confidence: {result['confidence']:.2%})")
    print("All probabilities:", result['all_probabilities'])