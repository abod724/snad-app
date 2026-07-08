import streamlit as st
from openai import OpenAI
import base64
from datetime import datetime

# -------------------------- إعدادات الصفحة --------------------------
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------- المفتاح --------------------------
API_KEY = st.secrets.get("OPENAI_API_KEY")

if not API_KEY:
    st.error("🔴 المفتاح غير مضاف في إعدادات Streamlit")
    st.stop()

client = OpenAI(api_key=API_KEY)

# -------------------------- CSS --------------------------
st.markdown("""
<style>
* {
    direction: rtl;
    text-align: right;
    font-family: 'Segoe UI', Tahoma, sans-serif;
}
.stApp {
    background: #ffffff;
    color: #1a1a1a;
}
#MainMenu, footer, header {visibility: hidden;}
.top-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: #ffffff;
    padding: 12px 25px;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
}
.top-left {
    display: flex;
    align-items: center;
    gap: 8px;
}
.top-left .heart {
    font-size: 28px;
    color: #dc2626;
}
.top-left .app-name {
    font-size: 24px;
    font-weight: 700;
    color: #1a1a1a;
}
.top-center p {
    margin: 0;
    font-size: 13px;
    color: #6b7280;
}
.chat-area {
    max-width: 850px;
    margin: 80px auto 100px;
}
.msg {
    padding: 12px 16px;
    margin: 6px 0;
    border-radius: 16px;
    max-width: 80%;
}
.user {
    background: #1a1a1a;
    color: #ffffff;
    margin-left: auto;
}
.bot {
    background: #f3f4f6;
    color: #1a1a1a;
}
div[data-testid="stChatInput"] {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    padding: 2px 12px !important;
}
div[data-testid="stChatInput"] input {
    color: #1a1a1a !important;
    font-weight: 500 !important;
    background: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------- الشريط العلوي --------------------------
st.markdown('<div class="top-bar">', unsafe_allow_html=True)
col_left, col_center, _ = st.columns([1.5, 2, 1.2])

with col_left:
    st.markdown('<div class="top-left"><span class="heart">❤️</span><span class="app-name">نبراس</span></div>', unsafe_allow_html=True)
with col_center:
    st.markdown('<div class="top-center"><p>مساعدك الذكي – بسيط، سريع، واضح</p></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- سجل المحادثة --------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "مرحبًا، أنا نبراس… كيف أقدر أساعدك اليوم؟"}]

st.markdown('<div class="chat-area">', unsafe_allow_html=True)
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg bot">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- مربع الكتابة --------------------------
user_input = st.chat_input("اكتب سؤالك هنا...")

# -------------------------- معالجة الإدخال --------------------------
if user_input:
    query = user_input.text.strip() if hasattr(user_input, 'text') else str(user_input).strip()
    if query:
        st.session_state.chat_history.append({"role": "user", "content": query})

        with st.spinner("🔍 جاري البحث..."):
            try:
                # ===== كود البحث الصحيح من OpenAI =====
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input="ابحث في الويب عن آخر تحديثات ChatGPT واذكر المصادر.",
                    tools=[{"type": "web_search"}],
                )

                answer = response.output_text

                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()

            except Exception as e:
                st.error(f"❌ خطأ: {str(e)}")
