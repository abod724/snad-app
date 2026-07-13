import streamlit as st
from openai import OpenAI
from googlesearch import search as google_search
from datetime import datetime

st.set_page_config(page_title="نبراس 2026", page_icon="📅", layout="wide")

API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود!")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ─── التاريخ الحقيقي ───
def get_current_date():
    return datetime.now().strftime("%A، %d %B %Y")

# ─── البحث في الويب ───
def search_web(query):
    try:
        results = list(google_search(query, num_results=3, lang="ar", stop=3))
        return "\n".join([f"• {r}" for r in results])
    except Exception as e:
        return ""

# ─── الشريط الجانبي ───
with st.sidebar:
    st.markdown("### ⚙️ الإعدادات")
    if st.button("➕ محادثة جديدة", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": "أنت نبراس، مساعد ذكي ومحدث. أجب بحد أقصى 3 جمل."},
            {"role": "assistant", "content": f"مرحباً! أنا نبراس، اليوم هو {get_current_date()}. كيف أساعدك؟"}
        ]
        st.rerun()
    st.divider()
    enable_search = st.toggle("🌐 بحث في الويب", value=True)
    st.caption(f"📅 التاريخ اليوم: {get_current_date()}")

# ─── المحادثة ───
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "أنت نبراس، مساعد ذكي ومحدث. أجب بحد أقصى 3 جمل."},
        {"role": "assistant", "content": f"مرحباً! أنا نبراس، اليوم هو {get_current_date()}. كيف أساعدك؟"}
    ]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# ─── مربع الكتابة ───
if prompt := st.chat_input("اكتب سؤالك..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            # ─── جاوب عن التاريخ مباشرة ───
            if "تاريخ" in prompt or "اليوم" in prompt:
                reply = f"اليوم هو {get_current_date()}."
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.stop()

            # ─── بحث في الويب ───
            search_context = ""
            if enable_search:
                with st.spinner("🌐 جاري البحث..."):
                    search_context = search_web(prompt)

            # ─── بناء التعليمات ───
            system_prompt = "أنت نبراس، مساعد ذكي ومحدث. أجب بحد أقصى 3 جمل."
            if search_context:
                system_prompt += f"\n\n📌 معلومات محدثة من البحث:\n{search_context}"

            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(st.session_state.messages)

            # ─── رد متقطع ───
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=200,
                temperature=0.3,
                stream=True
            )

            reply = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
