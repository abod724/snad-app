import streamlit as st
from openai import OpenAI
from googlesearch import search as google_search

st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود!")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ─── البحث في الويب ───
def search_web(query):
    try:
        results = list(google_search(query, num_results=3, lang="ar", stop=3))
        return "\n".join([f"• {r}" for r in results])
    except:
        return ""

# ─── الشريط الجانبي ───
with st.sidebar:
    st.markdown("### ⚙️ الإعدادات")
    if st.button("➕ محادثة جديدة", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": "أنت نبراس، مساعد مختصر. أجب بحد أقصى 3 جمل."},
            {"role": "assistant", "content": "مرحباً! أنا نبراس، كيف أساعدك اليوم؟"}
        ]
        st.rerun()
    st.divider()
    enable_search = st.toggle("🌐 بحث في الويب", value=True)

# ─── المحادثة ───
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "أنت نبراس، مساعد مختصر. أجب بحد أقصى 3 جمل."},
        {"role": "assistant", "content": "مرحباً! أنا نبراس، كيف أساعدك اليوم؟"}
    ]

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
            search_context = ""
            if enable_search:
                with st.spinner("🌐 جاري البحث..."):
                    search_context = search_web(prompt)

            system_prompt = "أنت نبراس، مساعد مختصر. أجب بحد أقصى 3 جمل."
            if search_context:
                system_prompt += f"\n\n📌 معلومات من البحث:\n{search_context}"

            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(st.session_state.messages)

            # ─── ✅ كلام متقطع ───
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=200,
                temperature=0.3,
                stream=True
            )

            reply = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
