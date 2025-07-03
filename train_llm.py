import os
import json
from tkinter import Tk, filedialog
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq
)
from datasets import load_dataset
from PyPDF2 import PdfReader

# ✅ Use file picker dialog
Tk().withdraw()  # Hide root window
print("📂 Please select your PDF files...")
pdf_paths = filedialog.askopenfilenames(
    title="Select PDF files",
    filetypes=[("PDF Files", "*.pdf")]
)

if not pdf_paths:
    print("❌ No PDF files selected. Exiting.")
    exit()

# ✅ Output path for JSONL
jsonl_path = "law_finetune_data.jsonl"
data = []

# ✅ Extract text and convert to instructions
for path in pdf_paths:
    reader = PdfReader(path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    sections = text.split("\n\n")
    for section in sections:
        if len(section.strip()) > 30:
            data.append({
                "instruction": f"Explain the following law:\n{section.strip()}",
                "output": f"This section is about: {section.strip()[:150]}..."
            })

# ✅ Save to JSONL
with open(jsonl_path, "w", encoding="utf-8") as f:
    for item in data:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"📄 Selected {len(pdf_paths)} PDF files.")
print(f"✅ Saved {len(data)} entries to {jsonl_path}")

# ✅ Load model/tokenizer
model_name = "google/flan-t5-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# ✅ Load dataset
dataset = load_dataset("json", data_files=jsonl_path, split="train")

# ✅ Format prompt/response
def format_prompt(example):
    return {
        "prompt": f"### Instruction:\n{example['instruction']}\n\n### Response:",
        "response": example["output"]
    }

formatted = dataset.map(format_prompt)

# ✅ Tokenize
def tokenize(example):
    input = tokenizer(example["prompt"], truncation=True, padding="max_length", max_length=512)
    output = tokenizer(example["response"], truncation=True, padding="max_length", max_length=128)
    input["labels"] = output["input_ids"]
    return input

tokenized = formatted.map(tokenize)

# ✅ Training arguments
training_args = TrainingArguments(
    output_dir="./llm_law_model",
    per_device_train_batch_size=2,
    num_train_epochs=3,
    logging_dir="./logs",
    save_strategy="epoch",
    logging_steps=10,
    report_to="none"
)

# ✅ Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized,
    tokenizer=tokenizer,
    data_collator=DataCollatorForSeq2Seq(tokenizer, model=model)
)

trainer.train()

# ✅ Save model
model.save_pretrained("./llm_law_model")
tokenizer.save_pretrained("./llm_law_model")

print("✅ Model training complete and saved.")
