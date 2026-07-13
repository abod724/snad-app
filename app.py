import streamlit as st
from openai import OpenAI
from datetime import datetime
import time

# ─── دالة الكتابة المتقطعة ───
def typewriter(text):
    placeholder = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        placeholder.write(displayed)
        time.sleep(0.01)

# ─── دالة التاريخ من جهازك ───
def get_real_date():
    return datetime.now().astimezone().strftime("%A، %d %B %Y")

# ─── حالة القائمة ───
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False

# ─── CSS ───
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
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title=" ", page_icon="", layout="wide")

API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود!")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ─── الأزرار العلوية ───
top_col1, top_col2, top_col3 = st.columns([0.1, 0.8, 0.1])

with top_col1:
    if st.button("≡"):
        st.session_state.menu_open = not st.session_state.menu_open

with top_col3:
    if st.button("+"):
        st.session_state.messages = []
        st.session_state.menu_open = False
        st.rerun()

# ─── القائمة المنسدلة ───
if st.session_state.menu_open:
    menu_box = st.container()
    with menu_box:
        st.markdown("""
        <div style="
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
        ">
        <b>القائمة</b><br><br>
        """, unsafe_allow_html=True)

        if st.button("إعدادات"):
            st.info("✔ تم فتح الإعدادات")

        if st.button("تغيير الثيم"):
            st.info("✔ سيتم إضافة الثيم لاحقًا")

        if st.button("حفظ المحادثة"):
            st.success("✔ تم حفظ المحادثة")

        if st.button("مسح المحادثة"):
            st.session_state.messages = []
            st.success("✔ تم مسح المحادثة")

        if st.button("معلومات التطبيق"):
            st.info("✔ هذا هو مساعد نبراس الذكي")

        st.markdown("</div>", unsafe_allow_html=True)

# ─── المحادثة ───
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("اسأل نبراس")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            if "اليوم" in prompt or "تاريخ" in prompt:
                reply = f"اليوم هو {get_real_date()}."
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            else:
                with st.spinner("جاري التفكير..."):
                    response = client.responses.create(
                        model="gpt-4o-mini",
                        input=[
                            {"role": "system", "content": "أنت مساعد نبراس الذكي. أجب بجمل قصيرة."},
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
