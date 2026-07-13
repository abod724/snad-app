import streamlit as st
from openai import OpenAI
from datetime import datetime

# ─── إخفاء الأيقونات عبر data-testid (يعمل في كل الإصدارات) ───
st.markdown("""
<style>
    /* إخفاء أيقونات المستخدم والمساعد نهائياً */
    [data-testid="stChatMessageAvatar"] {
        display: none !important;
    }
    /* تقليل المسافات بين الرسائل */
    .stChatMessage {
        gap: 0px !important;
        margin: 2px 0 !important;
    }
    /* خلفية بيضاء */
    .stApp {
        background: white !important;
    }
    /* إخفاء الهيدر والفوتر فقط (يبقي الشريط الجانبي) */
    header, footer {
        visibility: hidden !important;
    }
    /* جعل النص واضحاً */
    .stChatMessageContent {
        font-size: 15px !important;
        line-height: 1.6 !important;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title=" ",          # ← لا شيء يظهر في شريط المتصفح
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود!")
    st.stop()

client = OpenAI(api_key=API_KEY)

def get_current_date():
    return datetime.now().strftime("%A، %d %B %Y")

# ─── الشريط الجانبي (المنسدلة) ───
with st.sidebar:
    st.markdown("### ⚙️ الإعدادات")
    if st.button("➕ محادثة جديدة", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": "أنت مساعد ذكي ومحدث. أجب بجمل قصيرة ومختصرة (حد أقصى 3 جمل)."},
            {"role": "assistant", "content": f"مرحباً! اليوم هو {get_current_date()}."}
        ]
        st.rerun()
    st.divider()
    st.caption(f"📅 التاريخ اليوم: {get_current_date()}")

# ─── المحادثة ───
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "أنت مساعد ذكي ومحدث. أجب بجمل قصيرة ومختصرة."},
        {"role": "assistant", "content": f"مرحباً! اليوم هو {get_current_date()}."}
    ]

# ─── عرض الرسائل (بدون أيقونات بفضل CSS) ───
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# ─── مربع الكتابة ───
if prompt := st.chat_input("اكتب سؤالك..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            # ─── التاريخ مباشرة ───
            if "تاريخ" in prompt or "اليوم" in prompt:
                reply = f"اليوم هو {get_current_date()}."
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.stop()

            # ─── البحث بالويب ───
            with st.spinner("جاري التفكير..."):
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=[
                        {"role": "system", "content": "أنت مساعد ذكي ومحدث. أجب بجمل قصيرة ومختصرة (حد أقصى 3 جمل)."},
                        *st.session_state.messages
                    ],
                    tools=[{"type": "web_search"}],
                    max_output_tokens=200,
                    temperature=0.3
                )

                reply = response.output_text
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
