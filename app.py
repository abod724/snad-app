import streamlit as st
from openai import OpenAI
import os
import time
import base64

# ===== إعدادات الصفحة =====
st.set_page_config(page_title="نبراس", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# ===== المفتاح =====
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير مضاف")
    st.stop()
client = OpenAI(api_key=API_KEY)

# ===== الذاكرة =====
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def get_time():
    return time.strftime("%I:%M %p")

# ===== دالة لإضافة رسالة والرد =====
def add_message_and_reply(text):
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("assistant"):
        with st.spinner("نبراس يفكر..."):
            try:
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=st.session_state.messages,
                    tools=[{"type": "web_search"}],
                    max_output_tokens=500
                )
                reply = response.output_text
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ {str(e)}")

# ===== واجهة CSS الإبداعية =====
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #f5f7fa; }
.chat-container { max-width: 750px; margin: 80px auto 100px; padding: 0 20px; }

/* رسائل */
.msg-user {
    padding: 12px 18px; margin: 6px 0 6px auto; background: #e9ecef;
    border-radius: 20px 20px 4px 20px; max-width: 75%; width: fit-content;
    animation: slideInRight 0.3s ease;
}
.msg-bot {
    padding: 12px 18px; margin: 6px auto 6px 0; background: #ffffff;
    border-radius: 20px 20px 20px 4px; max-width: 75%; width: fit-content;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    animation: slideInLeft 0.3s ease;
}
@keyframes slideInRight { from { opacity:0; transform:translateX(20px); } to { opacity:1; transform:translateX(0); } }
@keyframes slideInLeft { from { opacity:0; transform:translateX(-20px); } to { opacity:1; transform:translateX(0); } }
.time-badge { font-size: 10px; color: #aaa; margin-top: 4px; display: block; }

/* الشريط العلوي */
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
.top-bar .new-chat-btn:hover { background: #333; transform: scale(1.02); }

/* أزرار الفئات (الإبداع) */
.category-grid {
    display: flex; gap: 12px; flex-wrap: wrap;
    justify-content: center; margin: 10px 0 20px 0;
}
.category-btn {
    background: white; border: 1px solid #e5e5e5;
    padding: 10px 24px; border-radius: 40px; font-size: 14px;
    cursor: pointer; transition: 0.3s; color: #1a1a1a;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02); flex: 1; min-width: 120px;
    text-align: center; font-weight: 500;
}
.category-btn:hover {
    background: #1a1a1a; color: white; border-color: #1a1a1a;
    transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

/* مربع الكتابة */
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

# ===== الشريط العلوي (بزر Streamlit حقيقي) =====
col1, col2 = st.columns([6, 1])
with col1:
    st.markdown('<div class="brand"><span>⚡</span> نبراس</div>', unsafe_allow_html=True)
with col2:
    if st.button("➕ دردشة جديدة", key="new_chat_top"):
        st.session_state.messages = []
        st.rerun()

# ===== عرض المحادثة =====
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">{msg["content"]}<span class="time-badge">{get_time()}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-bot">{msg["content"]}<span class="time-badge">{get_time()}</span></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ===== أزرار الفئات الإبداعية (تعمل فوراً) =====
st.markdown('<div class="category-grid">', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🤖 إبداع الذكاء الاصطناعي", key="cat_ai", use_container_width=True):
        add_message_and_reply("أعطني فكرة إبداعية في الذكاء الاصطناعي")

with col2:
    if st.button("📚 واجبات منزلية", key="cat_homework", use_container_width=True):
        add_message_and_reply("ساعدني في واجباتي المنزلية")

with col3:
    if st.button("💼 احترافي", key="cat_pro", use_container_width=True):
        add_message_and_reply("أريد رداً احترافياً")

st.markdown('</div>', unsafe_allow_html=True)

# ===== مربع الكتابة =====
prompt = st.chat_input("جار المراسلة...", key="main_chat")
if prompt:
    add_message_and_reply(prompt)
