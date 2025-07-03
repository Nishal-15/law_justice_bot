import json
import psycopg2
import psycopg2.extras


# 👇 Update path if needed
jsonl_path = "law_finetune_data.jsonl"

# 🔗 MySQL connection
conn = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="bot",
    database="law_chatbot"
)
cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


# 📥 Load and insert JSONL
with open(jsonl_path, "r", encoding="utf-8") as file:
    for line in file:
        entry = json.loads(line.strip())
        prompt = entry.get("prompt", "")
        completion = entry.get("completion", "")

        cursor.execute(
            "INSERT INTO chat_finetune_data (prompt, completion) VALUES (%s, %s)",
            (prompt, completion)
        )

conn.commit()
cursor.close()
conn.close()

print("✅ Data imported into chat_finetune_data table.")
