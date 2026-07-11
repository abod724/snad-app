import streamlit as st
from openai import OpenAI
import os
import time
import base64

st.set_page_config(page_title="نبراس", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير مضاف")
    st.stop()
client = OpenAI(api_key=API_KEY)

# ===== تهيئة الجلسة =====
if "messages" not in st.session_state:
    st.session_state.messages = []
if "waiting_for_response" not in st.session_state:
    st.session_state.waiting_for_response = False

def get_time():
    return time.strftime("%I:%M %p")

def add_user_message(text):
    """إضافة رسالة المستخدم وطلب رد واحد فقط"""
    st.session_state.messages.append({"role": "user", "content": text})
    st.session_state.waiting_for_response = True
    st.rerun()

def clear_chat():
    st.session_state.messages = []
    st.session_state.waiting_for_response = False
    st.rerun()

st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #f5f7fa; }
.chat-container { max-width: 750px; margin: 80px auto 100px; padding: 0 20px; }
.msg-user { padding: 12px 18px; margin: 6px 0 6px auto; background: #e9ecef; border-radius: 20px 20px 4px 20px; max-width: 75%; width: fit-content; }
.msg-bot { padding: 12px 18px; margin: 6px auto 6px 0; background: #ffffff; border-radius: 20px 20px 20px 4px; max-width: 75%; width: fit-content; box-shadow: 0 2px 12px rgba(0,0,0,0.04); }
.time-badge { font-size: 10px; color: #aaa; margin-top: 4px; display: block; }
.top-bar {
    position: fixed; top: 0; left: 0; right: 0;
    background: rgba(255,255,255,0.92); backdrop-filter: blur(12px);
    padding: 12px 24px; border-bottom: 1px solid rgba(0,0,0,0.04);
    display: flex; justify-content: space-between; align-items: center;
    z-index: 1000; height: 64px;
}
.top-bar .brand { font-size: 18px; font-weight: 600; color: #1a1a1a; }
.top-bar .brand span { background: #1a1a1a; color: white; border-radius: 50%; padding: 4px 10px; margin-left: 8px; font-size: 14px; }
.top-bar .new-chat-btn {
    background: #1a1a1a; color: white; border: none;
    padding: 8px 20px; border-radius: 30px; font-size: 14px;
    cursor: pointer; transition: 0.2s; font-weight: 500;
}
.category-grid { display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; margin: 10px 0 20px 0; }
.category-btn {
    background: white; border: 1px solid #e5e5e5; padding: 10px 24px;
    border-radius: 40px; font-size: 14px; cursor: pointer; transition: 0.3s;
    color: #1a1a1a; flex: 1; min-width: 120px; text-align: center;
}
.category-btn:hover { background: #1a1a1a; color: white; }
.stChatInput {
    border-radius: 40px !important; border: 1px solid rgba(0,0,0,0.04) !important;
    background: rgba(255,255,255,0.9) !important; backdrop-filter: blur(10px) !important;
    padding: 4px 16px !important;
    position: fixed !important; bottom: 20px !important; left: 50% !important;
    transform: translateX(-50%) !important;
    width: 750px !important; max-width: 94% !important; z-index: 999 !important;
}
.stChatInput input { border-radius: 40px !important; padding: 12px 16px !important; font-size: 15px !important; }
.stChatInput button { background: #1a1a1a !important; border-radius: 50% !important; padding: 6px 14px !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="top-bar">
    <div class="brand"><span>⚡</span> نبراس</div>
    <button class="new-chat-btn" onclick="location.reload()">➕ دردشة جديدة</button>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">{msg["content"]}<span class="time-badge">{get_time()}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-bot">{msg["content"]}<span class="time-badge">{get_time()}</span></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ===== أزرار الفئات =====
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🤖 إبداع", key="cat_ai", use_container_width=True):
        add_user_message("أريد فكرة إبداعية")
with col2:
    if st.button("📚 تعلم", key="cat_learn", use_container_width=True):
        add_user_message("أريد شرح درس")
with col3:
    if st.button("💼 محترف", key="cat_pro", use_container_width=True):
        add_user_message("أريد رداً احترافياً")

# ===== القائمة المنسدلة =====
quick_options = [
    "📝 تلخيص نص", "💡 فكرة مشروع", "📚 شرح درس", "🧠 حل مسألة",
    "✍️ كتابة مقال", "🌍 ترجمة", "🔍 بحث", "📊 تحليل",
    "🎨 تصميم", "📖 تعريف", "🗺️ خطة", "💼 سيرة ذاتية"
]

selected = st.selectbox("⚡ اختر خدمة سريعة:", quick_options, index=None, placeholder="📌 اختر من القائمة...")
if selected:
    add_user_message(selected)

# ===== مربع الكتابة =====
prompt = st.chat_input("اكتب سؤالك هنا...", key="main_chat")
if prompt:
    add_user_message(prompt)

# ===== معالجة الرد (مرة واحدة فقط) =====
if st.session_state.waiting_for_response and st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    st.session_state.waiting_for_response = False
    with st.spinner("نبراس يفكر..."):
        try:
            last_msg = st.session_state.messages[-1]["content"].lower()
            system_prompt = "أنت نبراس، مساعد ذكي ومختصر، تجيب في حدود 3 جمل."
            if "إبداع" in last_msg or "فكرة" in last_msg:
                system_prompt = "أنت نبراس، خبير إبداعي، تقدم فكرة واحدة ملهمة."
            elif "شرح" in last_msg or "درس" in last_msg:
                system_prompt = "أنت نبراس، معلم، تشرح الدرس في 3 نقاط."
            elif "بحث" in last_msg:
                system_prompt = "أنت نبراس، باحث، تقدم ملخصاً مختصراً."

            response = client.responses.create(
                model="gpt-4o-mini",
                input=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                tools=[{"type": "web_search"}],
                max_output_tokens=300
            )
            reply = response.output_text
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
            st.session_state.waiting_for_response = False
