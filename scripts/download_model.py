from transformers import AutoModelForSequenceClassification, AutoTokenizer

"""
This script downloads the model and tokenizer and saves them locally. It's used
during the build to prefetch model assets.
"""

model_name = "SamLowe/roberta-base-go_emotions"

# Download and cache the model and tokenizer
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

model_dir = 'model/'

# Save locally
model.save_pretrained(model_dir)
tokenizer.save_pretrained(model_dir)
