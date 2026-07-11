import streamlit as st
from openai import OpenAI
import os

# ============================================================
# إعدادات الصفحة
# ============================================================
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# استدعاء المفتاح من الأسرار
# ============================================================
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير مضاف")
    st.stop()
client = OpenAI(api_key=API_KEY)

# ============================================================
# ذاكرة المحادثة
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "أنت نبراس، صديق ذكي ودود، تجيب بأسلوب بسيط وواضح."},
        {"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}
    ]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ============================================================
# CSS للشريط العلوي
# ============================================================
st.markdown("""
<style>
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background: #f7f7f8; }

    /* الشريط العلوي */
    .top-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: #ffffff;
        padding: 8px 24px;
        border-bottom: 1px solid #e5e5e5;
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 1000;
        height: 50px;
    }

    .top-bar .left-btn, .top-bar .right-btn {
        background: transparent;
        border: none;
        font-size: 24px;
        cursor: pointer;
        padding: 4px 12px;
        border-radius: 50%;
        transition: 0.2s;
        color: #1a1a1a;
    }
    .top-bar .left-btn:hover, .top-bar .right-btn:hover {
        background: #f0f0f0;
    }

    /* منطقة المحادثة */
    .chat-container {
        max-width: 750px;
        margin: 70px auto 80px;
        padding: 0 20px;
    }

    /* رسائل */
    .msg-user {
        padding: 10px 16px;
        margin: 4px 0 8px auto;
        background: #e9ecef;
        border-radius: 18px;
        border-bottom-right-radius: 4px;
        max-width: 80%;
        width: fit-content;
        color: #1a1a1a;
        font-size: 15px;
        line-height: 1.6;
        clear: both;
    }
    .msg-bot {
        padding: 10px 16px;
        margin: 4px auto 8px 0;
        background: #ffffff;
        border-radius: 18px;
        border-bottom-left-radius: 4px;
        max-width: 80%;
        width: fit-content;
        color: #1a1a1a;
        font-size: 15px;
        line-height: 1.6;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        clear: both;
    }

    /* مربع الإدخال */
    .stChatInput {
        border-radius: 30px !important;
        border: 1px solid #e5e5e5 !important;
        background: #ffffff !important;
        padding: 2px 12px !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.02) !important;
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
        background: transparent !important;
    }
    .stChatInput button {
        background: #1a1a1a !important;
        border-radius: 50% !important;
        padding: 4px 12px !important;
        color: white !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# الشريط العلوي (أزرار Streamlit حقيقية)
# ============================================================
col_left, col_mid, col_right = st.columns([1, 6, 1])

with col_left:
    # زر ⊕ (محادثة جديدة)
    if st.button("⊕", key="new_chat_btn", help="محادثة جديدة"):
        st.session_state.messages = [
            {"role": "system", "content": "أنت نبراس، صديق ذكي ودود، تجيب بأسلوب بسيط وواضح."},
            {"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}
        ]
        st.rerun()

with col_right:
    # زر ☰ (المحادثات السابقة) - يفتح popover
    with st.popover("☰"):
        st.markdown("### 📋 المحادثات السابقة")
        if st.button("➕ محادثة جديدة", use_container_width=True):
            st.session_state.messages = [
                {"role": "system", "content": "أنت نبراس، صديق ذكي ودود، تجيب بأسلوب بسيط وواضح."},
                {"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}
            ]
            st.rerun()
        st.markdown("---")
        if st.session_state.chat_history:
            for i, chat in enumerate(st.session_state.chat_history[::-1]):
                if st.button(f"💬 محادثة {i+1}", key=f"pop_{i}", use_container_width=True):
                    st.session_state.messages = chat
                    st.rerun()
        else:
            st.info("لا توجد محادثات سابقة")

# ============================================================
# عرض المحادثة
# ============================================================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f'<div class="msg-bot">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# مربع الإدخال
# ============================================================
prompt = st.chat_input("اكتب سؤالك هنا...")

if prompt:
    # إضافة سؤال المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # الرد
    with st.chat_message("assistant"):
        with st.spinner("نبراس يبحث ويفكر..."):
            try:
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=st.session_state.messages,
                    tools=[{"type": "web_search"}],
                    max_output_tokens=500
                )
                reply = response.output_text
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

                # حفظ المحادثة الحالية في السجل
                st.session_state.chat_history.append(st.session_state.messages.copy())

            except Exception as e:
                st.error(f"⚠️ خطأ: {str(e)}")
