import streamlit as st
from openai import OpenAI
from datetime import datetime
import time

# ─── تأثير الكتابة المتقطعة ───
def typewriter(text):
    placeholder = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        placeholder.write(displayed)
        time.sleep(0.01)

# ─── حالة القائمة ───
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False

# ─── زر المنسدلة + زر محادثة جديدة ───
st.markdown("""
<style>
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    .stChatMessage {
        gap: 0px !important;
        margin: 2px 0 !important;
    }
    .stApp {
        background: white !important;
    }
    header, footer {
        visibility: hidden !important;
    }
    .stChatMessageContent {
        font-size: 15px !important;
        line-height: 1.6 !important;
    }

    /* حركة الانزلاق للقائمة */
    .menu-box {
        position: fixed;
        top: 50px;
        right: 10px;
        background: #ffffff;
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.2);
        z-index: 9999;
        width: 160px;
        font-size: 15px;
        transform: translateY(-20px);
        opacity: 0;
        transition: all 0.3s ease-in-out;
    }
    .menu-box.show {
        transform: translateY(0px);
        opacity: 1;
    }

    .menu-btn, .new-chat-btn {
        padding: 6px 10px;
        font-size: 20px;
        background-color: #f0f0f0;
        border: none;
        border-radius: 6px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# ─── أزرار Streamlit الحقيقية ───
col1, col2 = st.columns([0.1, 0.9])

with col1:
    if st.button("≡"):
        st.session_state.menu_open = not st.session_state.menu_open

with col2:
    if st.button("+"):
        st.session_state.messages = []
        st.session_state.menu_open = False
        st.rerun()

# ─── القائمة المنسدلة ───
menu_class = "menu-box show" if st.session_state.menu_open else "menu-box"

st.markdown(f"""
<div class="{menu_class}">
    <b>القائمة</b><br><br>
    • إعدادات<br>
    • تغيير الثيم<br>
    • حفظ المحادثة<br>
    • مسح المحادثة<br>
    • معلومات التطبيق<br>
</div>
""", unsafe_allow_html=True)

# ─── إعدادات الصفحة ───
st.set_page_config(page_title=" ", page_icon="", layout="wide")

API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود!")
    st.stop()

client = OpenAI(api_key=API_KEY)

def get_current_date():
    return datetime.now().strftime("%A، %d %B %Y")

# ─── المحادثة ───
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ─── مربع الكتابة ───
if prompt := st.chat_input("اكتب سؤالك..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            if "تاريخ" in prompt or "اليوم" in prompt:
                reply = f"اليوم هو {get_current_date()}."
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.stop()

            with st.spinner("جاري التفكير..."):
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=[
                        {"role": "system", "content": "أجب بجمل قصيرة."},
                        *st.session_state.messages
                    ],
                    tools=[{"type": "web_search"}],
                    max_output_tokens=200,
                    temperature=0.3
                )

                reply = response.output_text
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
