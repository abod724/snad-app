import streamlit as st
from openai import OpenAI
from datetime import datetime
import time

def typewriter(text):
    placeholder = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        placeholder.write(displayed)
        time.sleep(0.01)

def get_real_date():
    now = datetime.now()
    return now.strftime("%A، %d %B %Y")

# حالة القائمة
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False

# حالة الثيم
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# تطبيق الثيم
if st.session_state.theme == "dark":
    st.markdown("""
    <style>
        .stApp { background-color: #1e1e1e !important; }
        .stChatMessageContent { color: white !important; }
        .stButton>button { background-color: #333 !important; color: white !important; }
        .stTextInput>div>div>input { background-color: #333 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp { background-color: white !important; }
        .stChatMessageContent { color: black !important; }
        .stButton>button { background-color: #f0f0f0 !important; color: black !important; }
        .stTextInput>div>div>input { background-color: white !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# إخفاء الهيدر والفوتر
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

# أعلى الصفحة
top_col1, top_col2, top_col3 = st.columns([0.1, 0.8, 0.1])

with top_col1:
    if st.button("≡"):
        st.session_state.menu_open = not st.session_state.menu_open

with top_col2:
    if st.button("🌓 تبديل الثيم"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()

with top_col3:
    if st.button("+"):
        st.session_state.messages = []
        st.session_state.menu_open = False
        st.rerun()

# القائمة المنسدلة
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
            st.info("✔ استخدم زر 🌓 بالأعلى لتبديل الثيم")

        if st.button("حفظ المحادثة"):
            st.success("✔ تم حفظ المحادثة")

        if st.button("مسح المحادثة"):
            st.session_state.messages = []
            st.success("✔ تم مسح المحادثة")

        if st.button("معلومات التطبيق"):
            st.info("✔ هذا هو مساعد نبراس الذكي")

        if st.button("🔗 مشاركة التطبيق"):
            st.code("https://nibras-app-pp5.streamlit.app/", language="text")
            st.success("انسخ الرابط وشاركه مع من تحب 🌟")

        st.markdown("</div>", unsafe_allow_html=True)

# المحادثات
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("اسأل Nabras")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:

            # تعريف نبراس
            if ("من انت" in prompt) or ("عرف بنفسك" in prompt) or ("وش انت" in prompt) or ("من تكون" in prompt):
                reply = "أنا مساعد ذكاء اصطناعي تم تطويري وبرمجتي على يد أبو مشعل المطيري يعمل بالتأهيل الشامل بقسم الاتصالات الإدارية."
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.stop()

            # من برمجك؟
            if ("من برمجك" in prompt) or ("مين برمجك" in prompt) or ("من صنعك" in prompt) or ("من سواك" in prompt):
                reply = "أنا مساعد ذكاء اصطناعي تم تطويري وبرمجتي على يد أبو مشعل المطيري يعمل بالتأهيل الشامل بقسم الاتصالات الإدارية."
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.stop()

            # نبذة
            if ("عطني نبذه" in prompt) or ("عطني نبذة" in prompt) or ("نبذه عنك" in prompt):
                reply = "أنا مساعد ذكاء اصطناعي تم تطويري وبرمجتي على يد أبو مشعل المطيري يعمل بالتأهيل الشامل بقسم الاتصالات الإدارية."
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.stop()

            # ⭐ نظام التاريخ الجديد
            explicit_date = (
                "وش اليوم" in prompt or
                "كم التاريخ" in prompt or
                "اعطني التاريخ" in prompt or
                "اعطني اليوم" in prompt or
                "تاريخ اليوم" in prompt or
                "اليوم كم" in prompt
            )

            if explicit_date:
                reply = f"اليوم هو {get_real_date()}."
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.stop()

            # الرد الطبيعي
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
