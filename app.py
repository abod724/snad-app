import streamlit as st
from openai import OpenAI
from googlesearch import search as google_search

# ─── إعدادات الصفحة ───
st.set_page_config(
    page_title="نبراس - المساعد الذكي",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── استدعاء المفتاح من صندوق الأسرار ───
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود! أضفه في ملف .streamlit/secrets.toml")
    st.stop()

# ─── التنسيق ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
* { font-family: 'Tajawal', sans-serif; }
.main { background-color: #0e1117; }
.stChatMessage { border-radius: 16px; margin-bottom: 8px; }
[data-testid="stChatMessageContent"] { font-size: 16px; line-height: 1.8; }
.title-container { text-align: center; padding: 2rem 0 1rem; }
.title-container h1 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem;
    font-weight: 700;
}
.title-container p { color: #8899a6; font-size: 1.1rem; }
.sidebar .stTextInput > div > div > input { direction: ltr; }
</style>
""", unsafe_allow_html=True)

# ─── الشريط الجانبي ───
with st.sidebar:
    st.header("⚙️ الإعدادات")
    
    model = st.selectbox("🧠 النموذج", ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"], index=0)
    temperature = st.slider("🌡️ درجة الإبداع", 0.0, 2.0, 0.7, 0.1, help="قيمة أعلى = ردود أكثر إبداعاً")
    
    # ─── مفتاح البحث ───
    web_search = st.toggle("🌐 البحث في الويب", value=True, help="فعّل هذا الخيار للبحث عن معلومات حديثة")
    search_count = st.slider("📄 عدد النتائج", 3, 10, 5, key="sc", help="عدد نتائج البحث")
    
    system_prompt = st.text_area(
        "📝 شخصية المساعد",
        value="أنت نبراس، مساعد ذكي احترافي ودود. تجيب باللغة العربية بشكل واضح ومفصل ومنظم. استخدم الإيموجي عند الحاجة.",
        height=120
    )
    
    st.divider()
    if st.button("🗑️ مسح المحادثة", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.rerun()
    st.caption("صنع بـ ❤️ باستخدام Streamlit + OpenAI")

# ─── العنوان ───
st.markdown("""
<div class="title-container">
    <h1>🤖 نبراس</h1>
    <p>مدعوم بتقنية ChatGPT - اسألني أي شيء</p>
</div>
""", unsafe_allow_html=True)

# ─── تهيئة المحادثة ───
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─── عرض الرسائل السابقة ───
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

# ─── رسالة ترحيب ───
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown("مرحباً! 👋 أنا نبراس، مساعدك الذكي. كيف أقدر أساعدك اليوم؟")

# ─── دالة البحث ───
def search_google(query, max_results=5):
    try:
        results = list(google_search(query, num_results=max_results, advanced=True))
        if not results:
            return None
        context = ""
        for i, r in enumerate(results, 1):
            title = getattr(r, "title", "")
            desc = getattr(r, "description", "")
            url = getattr(r, "url", "")
            context += f"[{i}] {title}\n{desc}\nالرابط: {url}\n\n"
        return context.strip()
    except Exception as e:
        st.warning(f"⚠️ تعذر البحث: {e}")
        return None

# ─── إدخال المستخدم ───
if prompt := st.chat_input("اكتب رسالتك هنا..."):
    
    # ─── إضافة رسالة المستخدم وعرضها ───
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)
    
    # ─── البحث (إذا كان مفعّلاً) ───
    search_context = None
    if web_search:
        with st.spinner("🌐 جاري البحث..."):
            search_context = search_google(prompt, search_count)
    
    # ─── توليد الرد ───
    with st.chat_message("assistant", avatar="🤖"):
        try:
            client = OpenAI(api_key=API_KEY)
            
            # ─── بناء الرسائل ───
            messages_for_api = [{"role": "system", "content": system_prompt}]
            
            if search_context:
                messages_for_api.append({
                    "role": "system",
                    "content": f"📌 نتائج البحث:\n{search_context}\n\nاستخدم هذه المعلومات للإجابة، واذكر المصادر."
                })
            
            messages_for_api.extend(st.session_state.messages)
            
            # ─── التدفق ───
            stream = client.chat.completions.create(
                model=model,
                messages=messages_for_api,
                temperature=temperature,
                stream=True,
                max_tokens=4096
            )
            
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"❌ خطأ: {str(e)}")
