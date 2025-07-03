from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
import psycopg2

app = Flask(__name__)  # ✅ Corrected: use __name__, not name

# ✅ PostgreSQL connection using environment variables
def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "bot"),
        database=os.environ.get("DB_NAME", "law_chatbot"),
        port=os.environ.get("DB_PORT", "5432")
    )

# ✅ Local fine-tuned model path (change if needed)
model_path = "D:/bot/fine-tuned-lawbot"

if not os.path.isdir(model_path):
    raise ValueError(f"Model folder '{model_path}' not found.")

# ✅ Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

# ✅ Chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"answer": "❗ Please enter a valid question."})

    prompt = f"### Instruction:\n{message}\n\n### Response:\n"
    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=300)

    reply = tokenizer.decode(outputs[0], skip_special_tokens=True)
    answer = reply.split("### Response:")[-1].strip()

    return jsonify({"answer": answer})

# ✅ Health check endpoint
@app.route("/")
def home():
    return "<h2>✅ Law Chatbot LLM API is running!</h2>"

# ✅ Run the Flask app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway uses dynamic ports
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
