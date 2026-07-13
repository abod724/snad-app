from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import base64
import json

app = Flask(__name__)
CORS(app)

# ─── مفتاح OpenAI ───
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("⚠️  لم يتم العثور على OPENAI_API_KEY في المتغيرات البيئية")
    API_KEY = "sk-xxxxx"  # ضع مفتاحك هنا مؤقتاً للاختبار

client = OpenAI(api_key=API_KEY)

# ─── الصفحة الرئيسية ───
@app.route("/")
def index():
    return render_template("index.html")

# ─── نقطة نهاية المحادثة ───
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()
    images = data.get("images", [])  # قائمة صور base64

    if not user_message and not images:
        return jsonify({"reply": "الرجاء كتابة رسالة أو رفع صورة."})

    try:
        # ─── بناء الرسائل ───
        messages = [
            {"role": "system", "content": "أنت نبراس، مساعد ذكي ودود. تجيب بالعربية بوضوح وإيجاز."},
            {"role": "user", "content": user_message or "صف هذه الصورة"}
        ]

        # ─── إذا كانت هناك صور، استخدم GPT-4 Vision ───
        if images:
            content = [{"type": "text", "text": user_message or "صف هذه الصورة بالتفصيل"}]
            for img in images[:3]:  # حد أقصى 3 صور
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
            # ─── محادثة نصية عادية ───
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
