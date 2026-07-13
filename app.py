import streamlit as st
from openai import OpenAI
import base64
from io import BytesIO
from PIL import Image

# ─── إعدادات الصفحة ───
st.set_page_config(
    page_title="نبراس - مساعد ذكي",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── استدعاء المفتاح من الأسرار ───
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود! أضفه في ملف .streamlit/secrets.toml")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ─── تهيئة الجلسة ───
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "مرحباً! أنا نبراس، مساعدك الذكي. كيف أقدر أساعدك اليوم؟ 😊"}]

# ─── عرض المحادثة ───
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ─── رفع الصور (يظهر فوق مربع الكتابة) ───
col1, col2 = st.columns([0.2, 0.8])
with col1:
    st.markdown("📷")
    uploaded_images = st.file_uploader(
        "رفع صورة",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="image_uploader",
        label_visibility="collapsed"
    )

# ─── مربع الإدخال ───
prompt = st.chat_input("اكتب رسالتك...")

# ─── معالجة الرسالة ───
if prompt:
    # إضافة رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # معالجة الصور
    images_base64 = []
    if uploaded_images:
        for img in uploaded_images:
            bytes_data = img.getvalue()
            b64 = base64.b64encode(bytes_data).decode()
            images_base64.append(b64)

    # رد المساعد
    with st.chat_message("assistant"):
        try:
            # بناء الرسائل
            messages = [{"role": "system", "content": "أنت نبراس، مساعد ذكي ودود."}]
            messages.extend(st.session_state.messages)

            # إذا كان هناك صور، استخدم Vision API
            if images_base64:
                content = [{"type": "text", "text": prompt}]
                for b64 in images_base64[:3]:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                    })
                messages.append({"role": "user", "content": content})
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=800,
                    temperature=0.7
                )
                reply = response.choices[0].message.content
            else:
                # محادثة نصية عادية
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=800,
                    temperature=0.7
                )
                reply = response.choices[0].message.content

            st.write(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
