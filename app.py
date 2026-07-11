import streamlit as st
from openai import OpenAI
import os
import time
import base64
import requests
import json

# ============================================================
# إعدادات الصفحة
# ============================================================
st.set_page_config(
    page_title="نبراس",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# التحقق من المفتاح
# ============================================================
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير مضاف في الأسرار")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ============================================================
# تهيئة الجلسة
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "processing" not in st.session_state:
    st.session_state.processing = False

# ============================================================
# دوال مساعدة
# ============================================================
def get_time():
    return time.strftime("%I:%M %p")

def search_web(query):
    """بحث في الويب باستخدام Bing API (اختياري)"""
    try:
        BING_KEY = st.secrets.get("BING_API_KEY")
        if not BING_KEY:
            return ""
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": BING_KEY}
        params = {"q": query, "count": 3, "mkt": "ar-XA"}
        response = requests.get(url, headers=headers, params=params, timeout=5)
        data = response.json()
        results = []
        for item in data.get("webPages", {}).get("value", []):
            results.append(f"• {item['name']}: {item['snippet']}")
        return "\n".join(results) if results else ""
    except:
        return ""

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})
    st.session_state.processing = True
    st.rerun()

def clear_chat():
    st.session_state.messages = []
    st.session_state.processing = False
    st.rerun()

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #f5f7fa; }

.chat-container {
    max-width: 780px;
    margin: 70px auto 100px;
    padding: 0 20px;
}

.msg-user {
    padding: 12px 18px;
    margin: 6px 0 6px auto;
    background: #1a1a1a;
    color: white;
    border-radius: 20px 20px 4px 20px;
    max-width: 75%;
    width: fit-content;
    animation: slideInRight 0.3s ease;
}

.msg-bot {
    padding: 12px 18px;
    margin: 6px auto 6px 0;
    background: #ffffff;
    border-radius: 20px 20px 20px 4px;
    max-width: 75%;
    width: fit-content;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    animation: slideInLeft 0.3s ease;
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}

.time-badge {
    font-size: 10px;
    color: #aaa;
    margin-top: 4px;
    display: block;
}

.top-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(12px);
    padding: 8px 20px;
    border-bottom: 1px solid rgba(0,0,0,0.04);
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
    height: 56px;
}

.top-bar .btn-icon {
    background: transparent;
    border: none;
    font-size: 22px;
    cursor: pointer;
    padding: 6px 12px;
    border-radius: 50%;
    transition: 0.2s;
    color: #1a1a1a;
}
.top-bar .btn-icon:hover {
    background: #f0f0f0;
}

.top-bar .brand {
    font-weight: 600;
    font-size: 16px;
    color: #1a1a1a;
}

.stChatInput {
    border-radius: 40px !important;
    border: 1px solid rgba(0,0,0,0.04) !important;
    background: rgba(255,255,255,0.9) !important;
    backdrop-filter: blur(10px) !important;
    padding: 4px 16px !important;
    position: fixed !important;
    bottom: 20px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 760px !important;
    max-width: 94% !important;
    z-index: 999 !important;
}
.stChatInput input {
    border-radius: 40px !important;
    padding: 12px 16px !important;
    font-size: 15px !important;
    background: transparent !important;
}
.stChatInput button {
    background: #1a1a1a !important;
    border-radius: 50% !important;
    padding: 6px 14px !important;
    color: white !important;
    border: none !important;
}

.category-grid {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: center;
    margin: 10px 0 20px 0;
}
.category-btn {
    background: white;
    border: 1px solid #e5e5e5;
    padding: 8px 20px;
    border-radius: 30px;
    font-size: 13px;
    cursor: pointer;
    transition: 0.3s;
    color: #1a1a1a;
}
.category-btn:hover {
    background: #1a1a1a;
    color: white;
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# الشريط العلوي
# ============================================================
st.markdown("""
<div class="top-bar">
    <button class="btn-icon" onclick="location.reload()" title="محادثة جديدة">➕</button>
    <span class="brand">⚡ نبراس</span>
    <button class="btn-icon" onclick="alert('📋 المحادثات السابقة')" title="القائمة">☰</button>
</div>
""", unsafe_allow_html=True)

# ============================================================
# عرض المحادثة
# ============================================================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">{msg["content"]}<span class="time-badge">{get_time()}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-bot">{msg["content"]}<span class="time-badge">{get_time()}</span></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# أزرار الفئات
# ============================================================
st.markdown("""
<div class="category-grid">
    <span class="category-btn" onclick="document.querySelector('.stChatInput input').value='أعطني فكرة إبداعية'; setTimeout(() => document.querySelector('.stChatInput button').click(), 100);">🤖 إبداع</span>
    <span class="category-btn" onclick="document.querySelector('.stChatInput input').value='أريد شرح درس'; setTimeout(() => document.querySelector('.stChatInput button').click(), 100);">📚 تعلم</span>
    <span class="category-btn" onclick="document.querySelector('.stChatInput input').value='أريد رداً احترافياً'; setTimeout(() => document.querySelector('.stChatInput button').click(), 100);">💼 محترف</span>
    <span class="category-btn" onclick="document.querySelector('.stChatInput input').value='ما هي آخر أخبار التقنية؟'; setTimeout(() => document.querySelector('.stChatInput button').click(), 100);">📰 أخبار</span>
</div>
""", unsafe_allow_html=True)

# ============================================================
# مربع الكتابة
# ============================================================
prompt = st.chat_input("اكتب سؤالك هنا...", key="main_chat")

if prompt and not st.session_state.processing:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.processing = True
    st.rerun()

# ============================================================
# معالجة الرد
# ============================================================
if st.session_state.processing and st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    st.session_state.processing = False
    user_msg = st.session_state.messages[-1]["content"]

    with st.spinner("نبراس يفكر..."):
        try:
            # البحث في الويب
            web_results = search_web(user_msg)

            system_prompt = "أنت نبراس، مساعد ذكي ومختصر، تجيب بحد أقصى 3 جمل."
            if "فكرة" in user_msg or "إبداع" in user_msg:
                system_prompt = "أنت نبراس، خبير إبداعي، تقدم فكرة واحدة ملهمة."
            elif "شرح" in user_msg or "درس" in user_msg:
                system_prompt = "أنت نبراس، معلم، تشرح الدرس بأسلوب بسيط في نقاط."
            elif "أخبار" in user_msg or "تقنية" in user_msg:
                system_prompt = "أنت نبراس، باحث، تقدم ملخصاً محدثاً لأخبار التقنية."

            if web_results:
                system_prompt += f"\n\nمعلومات من البحث:\n{web_results}"

            response = client.responses.create(
                model="gpt-4o-mini",
                input=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                tools=[{"type": "web_search"}],
                max_output_tokens=400
            )

            reply = response.output_text
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
            st.session_state.processing = False
