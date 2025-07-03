from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import requests
import re
import os
from deep_translator import GoogleTranslator
from dotenv import load_dotenv  # Load environment variables from .env

load_dotenv()  # Load variables at runtime

app = Flask(__name__)  # ✅ Use __name__, not name
CORS(app)

# 🔗 PostgreSQL Connection (Render or Local)
conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "bot"),
    dbname=os.getenv("DB_NAME", "law_chatbot"),
    port=os.getenv("DB_PORT", "5432")
)
cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# 🤖 Call Ollama Mistral Model
def query_mistral(prompt):
    try:
        res = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        })
        res.raise_for_status()
        return res.json()["response"]
    except Exception as e:
        return f"⚠️ Mistral Error: {str(e)}"

# 🔍 Homepage Route
@app.route("/")
def index():
    return render_template("index.html")  # Make sure templates/index.html exists

# 💬 Chat Endpoint
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("message", "")
        language = data.get("language", "en")

        if not user_input:
            return jsonify({"answer": "❗ Please enter a valid question."})

        # 🌐 Translate to English if needed
        translated = GoogleTranslator(source='auto', target='en').translate(user_input) if language != "en" else user_input

        # 🔎 Search relevant law sections from DB
        words = re.findall(r'\w+', translated)
        like_query = " OR ".join(["content ILIKE %s"] * len(words))
        values = [f"%{w}%" for w in words]

        cursor.execute(f"SELECT * FROM law_sections WHERE {like_query} LIMIT 5", values)
        laws = cursor.fetchall()

        if not laws:
            return jsonify({"answer": "❌ Sorry, I couldn’t find relevant legal data for your question."})

        # 🧠 Combine legal context
        context = "\n\n".join([
            f"[{law['section']}] {law['title']} ({law['law']}):\n{law['content']}\nPunishment: {law['punishment']}\nFine: {law['fine']}"
            for law in laws
        ])

        # 📜 Prompt for LLM (Mistral)
        prompt = f"""
You are a senior Indian legal advisor.

A user asked: "{translated}"

Use the following legal data to answer clearly and professionally:
{context}

Respond with:

The relevant law and section number

Explanation of punishment and fine (if any)

A simplified explanation for the general public

Friendly tone, like you're helping a client
"""

        # ⚙️ Generate answer with Mistral
        result = query_mistral(prompt)

        # 🌐 Translate back to user's language if needed
        final = GoogleTranslator(source='en', target=language).translate(result) if language != "en" else result

        return jsonify({"answer": final})

    except Exception as e:
        return jsonify({"answer": f"❌ Server error: {str(e)}"}), 500

# ▶️ Run Flask and open browser automatically
if __name__ == "__main__":
    import webbrowser
    webbrowser.open("http://localhost:5000")  # Or 127.0.0.1
    app.run(host="0.0.0.0", port=5000, debug=True)
