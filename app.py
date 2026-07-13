import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS

# ─── إعدادات الصفحة ───
st.set_page_config(
    page_title="نبراس - مساعد ذكي",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── المفتاح من الأسرار ───
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود!")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ─── دوال البحث ───
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        if not results:
            return None
        context = ""
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            body = r.get("body", "")
            context += f"[{i}] {title}\n{body}\n\n"
        return context.strip()
    except:
        return None

# ─── الشريط الجانبي (المنسدلة) ───
with st.sidebar:
    st.markdown("## ⚙️ الإعدادات")
    
    # قائمة منسدلة لاختيار النموذج
    model = st.selectbox(
        "🧠 النموذج",
        ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        index=0
    )
    
    # شريط تمرير لدرجة الإبداع
    temperature = st.slider(
        "🌡️ الإبداع",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1
    )
    
    st.divider()
    
    # تفعيل البحث في الويب
    web_search = st.toggle("🌐 البحث في الويب", value=True)
    
    st.divider()
    
    # زر مسح المحادثة
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.caption(f"💬 الرسائل: {len(st.session_state.get('messages', []))}")

# ─── تهيئة المحادثة ───
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "مرحباً! أنا نبراس، مساعدك الذكي. كيف أقدر أساعدك اليوم؟ 😊"}]

# ─── عرض المحادثة ───
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ─── أدوات الإدخال (رفع الصور والصوت) ───
col1, col2, col3 = st.columns([1, 1, 8])

with col1:
    uploaded_images = st.file_uploader(
        "📷",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="img_uploader"
    )

with col2:
    audio_value = st.audio_input(
        "🎤",
        label_visibility="collapsed",
        key="audio_input"
    )

# ─── مربع الكتابة ───
with col3:
    prompt = st.chat_input("اكتب رسالتك هنا...")

# ─── معالجة الإدخال ───
if prompt:
    # إضافة رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            # ─── البحث في الويب ───
            search_context = None
            if web_search:
                with st.spinner("🌐 جاري البحث..."):
                    search_context = search_web(prompt)

            # ─── بناء التعليمات ───
            system_prompt = "أنت نبراس، مساعد ذكي ودود. تحدث بالعربية بوضوح."
            if search_context:
                system_prompt += f"\n\n📌 معلومات محدثة من البحث:\n{search_context}"

            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(st.session_state.messages)

            # ─── إذا كانت هناك صور مرفوعة ───
            if uploaded_images:
                # تحويل الصور إلى Base64
                import base64
                images_base64 = []
                for img in uploaded_images[:3]:
                    b64 = base64.b64encode(img.getvalue()).decode()
                    images_base64.append(b64)
                
                # إضافة الصور إلى الطلب (Vision)
                content = [{"type": "text", "text": prompt}]
                for b64 in images_base64:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                    })
                messages.append({"role": "user", "content": content})
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=600,
                    temperature=temperature
                )
                reply = response.choices[0].message.content
            else:
                # ─── محادثة نصية (مع تدفق) ───
                stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    stream=True,
                    max_tokens=500
                )
                reply = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
