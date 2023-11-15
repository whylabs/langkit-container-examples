from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import torch.nn.functional as F
from typing import List, Tuple, Any, Optional 
import pandas as pd


model: Optional[Any] = None
tokenizer: Optional[Any] = None


def load_model() -> None:
    global model
    global tokenizer
    model_path = "model/"
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)


labels = [
    "admiration",
    "amusement",
    "anger",
    "annoyance",
    "approval",
    "caring",
    "confusion",
    "curiosity",
    "desire",
    "disappointment",
    "disapproval",
    "disgust",
    "embarrassment",
    "excitement",
    "fear",
    "gratitude",
    "grief",
    "joy",
    "love",
    "nervousness",
    "optimism",
    "pride",
    "realization",
    "relief",
    "remorse",
    "sadness",
    "surprise",
]


def _map_probabilities_to_labels(probabilities: List[float]) -> List[Tuple[str, float]]:
    mapped_labels: List[Tuple[str, float]] = [it for it in zip(labels, probabilities)]
    mapped_labels.sort(key=lambda x: x[1], reverse=True)
    return mapped_labels


def inference(input_text: pd.Series) -> List[List[Tuple[str, float]]]:
    print(f'>>> running emotion inference on type "{type(input_text)}" "{input_text}"')
    if model is None or tokenizer is None:
        raise ValueError("Model not loaded. Please call load_model() first.")

    input_strings = [str(it) for it in input_text]
    inputs = tokenizer(input_strings, return_tensors="pt", truncation=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)

    # Apply softmax to convert logits to probabilities
    probs: List[List[float]] = F.softmax(outputs.logits, dim=1).numpy().tolist()
    return [_map_probabilities_to_labels(p) for p in probs]

