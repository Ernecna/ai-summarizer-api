# download_model.py
import os
from transformers import T5ForConditionalGeneration, T5Tokenizer

model_name = "t5-small"
output_dir = "./model_cache"

print(f"Downloading and saving model '{model_name}' to '{output_dir}'...")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

tokenizer.save_pretrained(output_dir)
model.save_pretrained(output_dir)

print("Model download and save complete.")