import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS

# ─── إعدادات الصفحة ───
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── المفتاح من الأسرار ───
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود!")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ─── البحث في الويب ───
def search_web(query, max_results=3):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return None
        context = ""
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            body = r.get("body", "")
            context += f"• {title}: {body[:200]}...\n"
        return context.strip()
    except:
        return None

# ─── الشريط الجانبي ───
with st.sidebar:
    st.markdown("### ⚙️ الإعدادات")
    if st.button("➕ محادثة جديدة", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": "أنت نبراس، مساعد مختصر ودقيق. أجب بحد أقصى 3 جمل."},
            {"role": "assistant", "content": "مرحباً! أنا نبراس، كيف أساعدك اليوم؟"}
        ]
        st.rerun()
    st.divider()
    enable_search = st.toggle("🌐 بحث في الويب", value=True)
    search_count = st.slider("عدد النتائج", 2, 5, 3)
    st.divider()
    st.caption(f"💬 الرسائل: {len(st.session_state.get('messages', [])) - 2}")
    st.caption("✂️ ردود مختصرة لتوفير الاستهلاك")

# ─── المحادثة ───
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "أنت نبراس، مساعد مختصر ودقيق. أجب بحد أقصى 3 جمل."},
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
            # ─── بحث ───
            search_context = None
            if enable_search:
                with st.spinner("🌐 جاري البحث..."):
                    search_context = search_web(prompt, search_count)

            # ─── التعليمات ───
            system_prompt = "أنت نبراس، مساعد مختصر ودقيق. أجب بحد أقصى 3 جمل."
            if search_context:
                system_prompt += f"\n\n📌 معلومات محدثة:\n{search_context}"

            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(st.session_state.messages)

            # ─── ✅ هنا الكلام المتقطع (Streaming) ───
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=200,
                temperature=0.3,
                stream=True  # ← هذا السطر يخلّي الرد يكتب كلمة كلمة
            )

            reply = st.write_stream(stream)  # ← وهنا يظهر التأثير
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
