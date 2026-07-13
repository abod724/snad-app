from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

# ─── محاولة قراءة المفتاح من ملف .streamlit/secrets.toml ───
def get_secret(key):
    try:
        import tomllib
        with open(".streamlit/secrets.toml", "rb") as f:
            secrets = tomllib.load(f)
            return secrets.get(key)
    except:
        return os.getenv(key)  # أو من متغير البيئة

API_KEY = get_secret("OPENAI_API_KEY")
if not API_KEY:
    raise Exception("❌ لم يتم العثور على OPENAI_API_KEY في secrets.toml أو البيئة.")

client = OpenAI(api_key=API_KEY)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()
    images = data.get("images", [])

    if not user_message and not images:
        return jsonify({"reply": "الرجاء كتابة رسالة أو رفع صورة."})

    try:
        messages = [
            {"role": "system", "content": "أنت نبراس، مساعد ذكي ودود."},
            {"role": "user", "content": user_message or "صِف هذه الصورة"}
        ]

        if images:
            content = [{"type": "text", "text": user_message or "صِف هذه الصورة بالتفصيل"}]
            for img in images[:3]:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img}"}
                })
            messages.append({"role": "user", "content": content})
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )
        else:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"⚠️ خطأ: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
