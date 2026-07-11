import streamlit as st
from openai import OpenAI
import os
import time
import base64
import requests

st.set_page_config(page_title="نبراس", page_icon="⚡", layout="wide")

API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.warning("🔑 أضف مفتاح OpenAI في الأسرار (secrets).")
    API_KEY = st.text_input("أدخل مفتاح OpenAI مؤقتاً:", type="password")
    if not API_KEY:
        st.stop()
    else:
        st.success("✅ مفتاح مؤقت مفعل!")
        client = OpenAI(api_key=API_KEY)
else:
    client = OpenAI(api_key=API_KEY)

# ===== تهيئة الجلسة =====
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_time():
    return time.strftime("%I:%M %p")

# ===== الشريط العلوي (بأزرار Streamlit الأصلية) =====
col1, col2, col3 = st.columns([1, 6, 1])

with col1:
    if st.button("➕", key="new_chat", help="محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()

with col2:
    st.markdown('<div style="text-align:center; font-weight:600; font-size:18px;">⚡ نبراس</div>', unsafe_allow_html=True)

with col3:
    with st.popover("☰", help="القائمة"):
        st.markdown("### 📋 القائمة")
        if st.button("🗑️ مسح المحادثة", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        st.markdown("---")
        st.info(f"📊 عدد الرسائل: {len(st.session_state.messages)}")

# ===== عرض المحادثة =====
st.markdown('<div style="max-width: 760px; margin: 70px auto 100px; padding: 0 20px;">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"] + f"\n\n<small style='color:#aaa;'>{get_time()}</small>", unsafe_allow_html=True)
    else:
        st.chat_message("assistant").write(msg["content"] + f"\n\n<small style='color:#aaa;'>{get_time()}</small>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ===== منطقة الأدوات ومربع الكتابة =====
with st.container():
    # صف يحتوي على أيقونات رفع الملف والصوت (فوق مربع الكتابة مباشرة)
    col_tools1, col_tools2, col_tools3 = st.columns([1, 1, 10])
    
    with col_tools1:
        uploaded_file = st.file_uploader(
            "📎", 
            type=["jpg", "jpeg", "png", "pdf", "txt", "csv"],
            label_visibility="collapsed",
            key="file_uploader_main"
        )
        if uploaded_file:
            st.success(f"✅ {uploaded_file.name}")

    with col_tools2:
        audio_value = st.audio_input(
            "🎤", 
            label_visibility="collapsed",
            key="audio_input_main"
        )
        if audio_value:
            st.success("✅ تم تسجيل الصوت! (يمكنك تحويله باستخدام Whisper)")

    # مربع الكتابة الرئيسي
    prompt = st.chat_input("اكتب سؤالك هنا...", key="main_chat")

# ===== معالجة الإدخال =====
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("نبراس يفكر..."):
            try:
                # استدعاء ذكاء اصطناعي بسيط (مع بحث ويب)
                system_prompt = "أنت نبراس، مساعد ذكي ومختصر، تجيب في حدود 3 جمل."
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                    tools=[{"type": "web_search"}],
                    max_output_tokens=400
                )
                reply = response.output_text
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.write(reply)
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ خطأ: {str(e)}")
