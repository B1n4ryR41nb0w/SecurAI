from transformers import DistilRoBERTaTokenizer, DistilRoBERTaForSequenceClassification, Trainer, TrainingArguments
import pandas as pd
import os
from pathlib import Path

# Resolve project root (two levels up from this script)
project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = project_root / "data" / "classifier_data.csv"
MODEL_OUTPUT_DIR = project_root / "models" / "distilroberta_bug_classifier"

# Ensure the model output directory exists
MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def prepare_dataset():
    """Load and preprocess the dataset for fine-tuning."""
    df = pd.read_csv(DATA_PATH)
    tokenizer = DistilRoBERTaTokenizer.from_pretrained("distilroberta-base")

    # Tokenize descriptions
    inputs = tokenizer(df["Description"].tolist(), padding=True, truncation=True, max_length=128, return_tensors="pt")

    # Map severity to labels (0=Low, 1=Medium, 2=High)
    labels = [0 if s == "Low" else 1 if s == "Medium" else 2 for s in df["Severity"]]

    return {
        "input_ids": inputs["input_ids"],
        "attention_mask": inputs["attention_mask"],
        "labels": labels
    }


def fine_tune_model():
    """Fine-tune DistilRoBERTa on the dataset."""
    model = DistilRoBERTaForSequenceClassification.from_pretrained("distilroberta-base", num_labels=3)
    dataset = prepare_dataset()

    training_args = TrainingArguments(
        output_dir=MODEL_OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=8,
        save_steps=10_000,
        evaluation_strategy="no",  # No validation split for simplicity (use all data for training)
        logging_dir="./logs",  # Optional: log training progress
        logging_steps=10,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset
    )

    # Train the model
    trainer.train()

    # Save the fine-tuned model and tokenizer
    model.save_pretrained(MODEL_OUTPUT_DIR)
    tokenizer.save_pretrained(MODEL_OUTPUT_DIR)
    print(f"Model fine-tuned and saved to {MODEL_OUTPUT_DIR}")


if __name__ == "__main__":
    fine_tune_model()