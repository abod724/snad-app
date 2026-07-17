import streamlit as st
import time
from groq import Groq
from openai import OpenAI
import requests

# ============================
# 1) إعدادات المفاتيح والمحركات
# ============================

OPENAI_KEY = st.secrets.get("OPENAI_API_KEY")
GROQ_KEY = st.secrets.get("GROQ_API_KEY")

openai_client = OpenAI(api_key=OPENAI_KEY)
groq_client = Groq(api_key=GROQ_KEY)

# ============================
# 2) اختيار موديلات Groq الجديدة
# ============================

def get_latest_groq_model():
    try:
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        response = requests.get("https://api.groq.com/openai/v1/models", headers=headers).json()
        models = response.get("data", [])

        allowed = [
            m["id"] for m in models
            if any(x in m["id"] for x in [
                "llama3-8b-1m",
                "llama3-70b-1m",
                "llama3-70b-8192",
                "mixtral",
                "gemma2"
            ])
        ]

        return allowed[-1] if allowed else "llama3-70b-8192"

    except:
        return "llama3-70b-8192"

latest_model = get_latest_groq_model()

# ============================
# 3) دالة البحث بالويب
# ============================

def web_search(query):
    serp_key = st.secrets.get("SERPAPI_API_KEY")
    if not serp_key:
        return "لا يوجد مفتاح بحث ويب."
    url = f"https://serpapi.com/search?q={query}&engine=google&api_key={serp_key}"
    data = requests.get(url).json()
    results = data.get("organic_results", [])
    text = ""
    for r in results[:5]:
        text += f"- {r.get('title')}: {r.get('snippet')}\n"
    return text if text else "لا توجد نتائج."

# ============================
# 4) دالة الكتابة المتدرجة
# ============================

def typewriter(text):
    placeholder = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        placeholder.write(displayed)
        time.sleep(0.01)

# ============================
# 5) واجهة Streamlit
# ============================

st.set_page_config(page_title="Nabras", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

engine = st.selectbox("اختر المحرك", ["Groq", "OpenAI"])

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ============================
# 6) استقبال الرسائل
# ============================

prompt = st.chat_input("اسأل Nabras")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:

            # ============================
            # منع ذكر المؤسس أو المطور
            # ============================

            founder_keywords = [
                "من اسسك", "مين اسسك", "من طورك", "مين طورك",
                "من برمجك", "مين برمجك", "من جهتك", "وش جهتك",
                "من صانعك", "مين صانعك", "من سواك", "مين سواك",
                "من مطورك", "مين مطورك", "من صنعك", "مين صنعك",
                "من ابتكرك", "من ابتكر نبراس", "من صممك"
            ]

            if any(k in prompt for k in founder_keywords):
                reply = "أنا مساعد نبراس الذكي ولا أذكر معلومات عن من أسسني أو طورني."
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.stop()

            # ============================
            # بحث ويب
            # ============================

            search_results = web_search(prompt)

            # ============================
            # الردود حسب المحرك
            # ============================

            if engine == "OpenAI":
                response = openai_client.responses.create(
                    model="gpt-4o-mini",
                    input=[
                        {"role": "system", "content": f"استخدم نتائج البحث:\n{search_results}"},
                        *st.session_state.messages
                    ],
                    max_output_tokens=200,
                    temperature=0.3
                )
                reply = response.output_text

            else:
                response = groq_client.chat.completions.create(
                    model=latest_model,
                    messages=[
                        {"role": "system", "content": f"""
استخدم نتائج البحث:
{search_results}

اكتب ردًا واضحًا، دقيقًا، بدون تكرار.
                        """},
                        *st.session_state.messages
                    ]
                )
                reply = response.choices[0].message.content

            typewriter(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
