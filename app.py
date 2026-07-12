import streamlit as st
from openai import OpenAI

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

[data-testid="stChatMessageContent"] {
    font-size: 16px;
    line-height: 1.8;
}

.title-container {
    text-align: center;
    padding: 2rem 0 1rem;
}

.title-container h1 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem;
    font-weight: 700;
}

.title-container p {
    color: #8899a6;
    font-size: 1.1rem;
}
</style>
""", unsafe_allow_html=True)

# ─── الشريط الجانبي ───
with st.sidebar:
    st.header("⚙️ الإعدادات")
    
    model = st.selectbox(
        "🧠 النموذج",
        ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        index=0
    )
    
    temperature = st.slider(
        "🌡️ درجة الإبداع",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="قيمة أعلى = ردود أكثر إبداعاً"
    )
    
    system_prompt = st.text_area(
        "📝 شخصية المساعد",
        value="أنت نبراس، مساعد ذكي احترافي ودود. تجيب باللغة العربية بشكل واضح ومفصل ومنظم. استخدم الإيموجي عند الحاجة. ابحث في الويب إذا كان السؤال يحتاج معلومات حديثة.",
        height=120
    )
    
    st.divider()
    
    if st.button("🗑️ مسح المحادثة", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.rerun()

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

# ─── إدخال المستخدم ───
if prompt := st.chat_input("اكتب رسالتك هنا..."):
    
    # إضافة رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)
    
    # توليد الرد
    with st.chat_message("assistant", avatar="🤖"):
        try:
            client = OpenAI(api_key=API_KEY)
            
            messages_for_api = [{"role": "system", "content": system_prompt}]
            messages_for_api.extend(st.session_state.messages)
            
            # ─── استخدام Responses API مع بحث ويب و Streaming ───
            stream = client.responses.create(
                model=model,
                input=messages_for_api,
                tools=[{"type": "web_search"}],
                stream=True,
                max_output_tokens=4096,
                temperature=temperature
            )
            
            # تجميع الرد من التدفق
            full_response = ""
            for chunk in stream:
                if chunk.type == "response.output_text.delta":
                    full_response += chunk.delta
                    st.write(chunk.delta)  # عرض تدريجي
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "auth" in error_msg.lower():
                st.error("❌ مفتاح API غير صالح. تأكد من صحة المفتاح في ملف الأسرار.")
            elif "rate_limit" in error_msg.lower():
                st.error("⏳ تم تجاوز حد الاستخدام. انتظر قليلاً وحاول مجدداً.")
            elif "model" in error_msg.lower():
                st.error(f"❌ النموذج '{model}' غير متاح في حسابك. جرب نموذج آخر.")
            else:
                st.error(f"❌ حصل خطأ: {error_msg}")
