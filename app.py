import streamlit as st
from openai import OpenAI
import os

st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير مضاف")
    st.stop()

client = OpenAI(api_key=API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "أنت نبراس، صديق ذكي ودود."},
        {"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}
    ]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ===== الشريط الجانبي =====
with st.sidebar:
    st.markdown("### 💬 نبراس")
    if st.button("➕ محادثة جديدة", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": "أنت نبراس، صديق ذكي ودود."},
            {"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}
        ]
        st.rerun()
    st.markdown("### 📋 المحادثات السابقة")
    if st.session_state.chat_history:
        for i, chat in enumerate(st.session_state.chat_history[::-1]):
            if st.button(f"💬 محادثة {i+1}", key=f"side_{i}"):
                st.session_state.messages = chat
                st.rerun()
    else:
        st.info("لا توجد محادثات سابقة")

# ===== CSS =====
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #f7f7f8; }
.chat-container { max-width: 750px; margin: 20px auto; padding: 0 20px; }
.msg-user {
    padding: 10px 16px;
    margin: 4px 0 8px auto;
    background: #e9ecef;
    border-radius: 18px;
    max-width: 80%;
    width: fit-content;
}
.msg-bot {
    padding: 10px 16px;
    margin: 4px auto 8px 0;
    background: #ffffff;
    border-radius: 18px;
    max-width: 80%;
    width: fit-content;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.stChatInput {
    border-radius: 30px !important;
    border: 1px solid #e5e5e5 !important;
    background: #ffffff !important;
    padding: 2px 12px !important;
    position: fixed !important;
    bottom: 20px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 750px !important;
    max-width: 92% !important;
    z-index: 999 !important;
}
.stChatInput input {
    border-radius: 30px !important;
    padding: 12px 16px !important;
    font-size: 15px !important;
}
.stChatInput button {
    background: #1a1a1a !important;
    border-radius: 50% !important;
    padding: 4px 12px !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ===== عرض المحادثة =====
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f'<div class="msg-bot">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ===== أيقونة فوق المدخل =====
st.markdown("""
<div style="text-align:center; margin-bottom:4px;">
    <span style="font-size:28px;">👦</span>
</div>
""", unsafe_allow_html=True)

# ===== الإدخال (مع key لتجنب التعارض) =====
prompt = st.chat_input("اكتب سؤالك هنا...", key="main_chat")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

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
                st.session_state.chat_history.append(st.session_state.messages.copy())
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ خطأ: {str(e)}")
