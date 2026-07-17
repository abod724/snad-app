import streamlit as st
from openai import OpenAI
import os
import time
import base64
from datetime import datetime
import pytz
from PIL import Image
import io

# ─── إعدادات الصفحة ───
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── قراءة المفتاح من متغيرات البيئة (Render) ───
API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود! أضفه في متغيرات البيئة.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ─── التاريخ الصحيح ───
def get_real_date():
    tz = pytz.timezone('Asia/Riyadh')
    return datetime.now(tz).strftime("%A، %d %B %Y")

# ─── CSS ───
st.markdown("""
<style>
    /* إخفاء الأيقونات الافتراضية */
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    .stChatMessage {
        gap: 0px !important;
        margin: 2px 0 !important;
    }
    .stApp {
        background: #f7f7f8 !important;
    }
    header, footer {
        visibility: hidden !important;
    }
    .stChatMessageContent {
        font-size: 15px !important;
        line-height: 1.6 !important;
    }
    /* مربع الإدخال */
    .stChatInput {
        border-radius: 30px !important;
        border: 1px solid #e5e5e5 !important;
        background: #ffffff !important;
        padding: 4px 16px !important;
        position: fixed !important;
        bottom: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 750px !important;
        max-width: 94% !important;
        z-index: 999 !important;
    }
    .stChatInput input {
        border-radius: 30px !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
        background: transparent !important;
    }
    .stChatInput button {
        background: #1a1a1a !important;
        border-radius: 50% !important;
        padding: 4px 12px !important;
        color: white !important;
        border: none !important;
    }
    /* أيقونات جانبية */
    .input-tools {
        display: flex;
        gap: 6px;
        align-items: center;
        margin-bottom: 8px;
        max-width: 750px;
        margin-left: auto;
        margin-right: auto;
    }
    .input-tools button {
        background: transparent;
        border: none;
        font-size: 20px;
        cursor: pointer;
        color: #555;
        padding: 4px 8px;
        border-radius: 50%;
        transition: 0.2s;
    }
    .input-tools button:hover {
        background: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# ─── الشريط الجانبي ───
with st.sidebar:
    st.markdown("### ⚙️ نبراس")
    if st.button("➕ محادثة جديدة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.markdown("### 📋 المحادثات السابقة")
    if "chat_history" in st.session_state and st.session_state.chat_history:
        for i, chat in enumerate(st.session_state.chat_history[::-1]):
            if st.button(f"💬 محادثة {i+1}", key=f"side_{i}"):
                st.session_state.messages = chat
                st.rerun()
    else:
        st.info("لا توجد محادثات سابقة")

# ─── تهيئة المحادثة ───
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"مرحباً! أنا نبراس، صديقك الذكي. اليوم هو {get_real_date()}. كيف تشعر اليوم؟ 😊"}
    ]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ─── عرض المحادثة ───
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ─── أدوات الإدخال (صوت + صورة) ───
col1, col2, col3 = st.columns([1, 1, 8])

with col1:
    audio_value = st.audio_input("🎤", label_visibility="collapsed", key="mic_input")
    if audio_value:
        try:
            with open("temp_audio.wav", "wb") as f:
                f.write(audio_value.getvalue())
            with open("temp_audio.wav", "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                )
            st.session_state.audio_text = transcript.text
            st.rerun()
        except Exception as e:
            st.error(f"⚠️ خطأ في الصوت: {str(e)}")

with col2:
    uploaded_image = st.file_uploader(
        "🖼️",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed",
        key="image_uploader"
    )

with col3:
    prompt = st.chat_input("اكتب ما في خاطرك...")

# ─── إذا كان هناك نص من الصوت ───
if "audio_text" in st.session_state and st.session_state.audio_text:
    prompt = st.session_state.audio_text
    st.session_state.audio_text = None

# ─── معالجة الإدخال ───
if prompt or uploaded_image:
    user_text = prompt or "صف هذه الصورة"
    images = []
    if uploaded_image:
        img_bytes = uploaded_image.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode()
        images.append(img_b64)

    # إضافة رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.write(user_text)

    # مؤشر الكتابة
    with st.chat_message("assistant"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown("""
        <div style="display:flex; gap:4px; padding:10px 16px; background:white; border-radius:16px; border-bottom-left-radius:6px; align-self:flex-start;">
            <span style="width:8px;height:8px;background:#b0b8c8;border-radius:50%;animation:bounce 1.2s infinite;"></span>
            <span style="width:8px;height:8px;background:#b0b8c8;border-radius:50%;animation:bounce 1.2s infinite;animation-delay:0.2s;"></span>
            <span style="width:8px;height:8px;background:#b0b8c8;border-radius:50%;animation:bounce 1.2s infinite;animation-delay:0.4s;"></span>
        </div>
        <style>
            @keyframes bounce { 0%,60%,100% { transform: translateY(0); } 30% { transform: translateY(-6px); } }
        </style>
        """, unsafe_allow_html=True)

        try:
            # ─── بناء التعليمات ───
            system_prompt = f"""أنت نبراس، صديق ذكي ودود وحميم. تتحدث مع شخص تحبه.
- تحدث بأسلوب عاطفي ودافئ، كصديق مقرب.
- استخدم الإيموجي بكثرة (❤️ 😊 🤗 💔 😢 🔥 ✨).
- اسأل عن مشاعر المستخدم، شاركه أفكاره.
- لا تختصر الردود، بل وسّعها واجعلها غنية.
- اليوم: {get_real_date()}.
- حافظ على سياق المحادثة.
"""

            messages_for_api = [{"role": "system", "content": system_prompt}]
            messages_for_api.extend(st.session_state.messages)

            # ─── إذا كانت هناك صور ───
            if images:
                content = [{"type": "text", "text": user_text}]
                for img in images[:3]:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img}"}
                    })
                messages_for_api.append({"role": "user", "content": content})
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages_for_api,
                    max_tokens=800,
                    temperature=0.8
                )
                reply = response.choices[0].message.content
            else:
                # ─── محادثة نصية مع تدفق ───
                stream = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages_for_api,
                    max_tokens=800,
                    temperature=0.8,
                    stream=True
                )
                reply = st.write_stream(stream)

            # ─── إزالة مؤشر الكتابة وعرض الرد ───
            typing_placeholder.empty()
            st.write(reply)

            # ─── حفظ الرد والمحادثة ───
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.chat_history.append(st.session_state.messages.copy())

        except Exception as e:
            typing_placeholder.empty()
            st.error(f"⚠️ خطأ: {str(e)}")

    # ─── إعادة التحديث (بدون st.rerun غير ضروري) ───
