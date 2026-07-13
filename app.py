import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import time
import re
from datetime import datetime

# ─── إعدادات الصفحة ───
st.set_page_config(
    page_title="نبراس X",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── المفتاح من الأسرار ───
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود!")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ─── CSS واجهة احترافية (مثل ChatGPT) ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');
    
    * { font-family: 'Tajawal', sans-serif; }
    
    .stApp {
        background: #0e1117;
    }
    
    /* إخفاء العناصر الزائدة */
    #MainMenu, footer, header { visibility: hidden; }
    
    /* الشريط العلوي */
    .top-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: rgba(14, 17, 23, 0.92);
        backdrop-filter: blur(12px);
        padding: 10px 24px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 1000;
        height: 60px;
    }
    .top-bar .brand {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 18px;
        font-weight: 700;
        color: #ffffff;
    }
    .top-bar .brand .icon {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 6px 12px;
        border-radius: 10px;
        font-size: 16px;
    }
    .top-bar .status {
        color: #8e8ea0;
        font-size: 13px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .top-bar .status .dot {
        width: 8px;
        height: 8px;
        background: #4ade80;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
    
    .top-bar .actions {
        display: flex;
        gap: 6px;
    }
    .top-bar .actions button {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        color: #ffffff;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        cursor: pointer;
        transition: 0.2s;
    }
    .top-bar .actions button:hover {
        background: rgba(255,255,255,0.12);
    }
    
    /* منطقة المحادثة */
    .chat-container {
        max-width: 800px;
        margin: 80px auto 100px;
        padding: 0 20px;
    }
    
    /* فقاعات المحادثة */
    .msg-user {
        padding: 12px 18px;
        margin: 6px 0 6px auto;
        background: #1a1a1a;
        color: #ffffff;
        border-radius: 20px 20px 4px 20px;
        max-width: 75%;
        width: fit-content;
        animation: slideInRight 0.3s ease;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .msg-bot {
        padding: 12px 18px;
        margin: 6px auto 6px 0;
        background: #1e1e2a;
        color: #ececf1;
        border-radius: 20px 20px 20px 4px;
        max-width: 75%;
        width: fit-content;
        animation: slideInLeft 0.3s ease;
        border: 1px solid rgba(255,255,255,0.04);
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
        color: #6b6b80;
        margin-top: 4px;
        display: block;
    }
    
    /* مربع الإدخال */
    .stChatInput {
        border-radius: 30px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        background: rgba(255,255,255,0.04) !important;
        padding: 4px 16px !important;
        position: fixed !important;
        bottom: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 760px !important;
        max-width: 94% !important;
        z-index: 999 !important;
        backdrop-filter: blur(10px) !important;
    }
    .stChatInput input {
        border-radius: 30px !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
        background: transparent !important;
        color: #ffffff !important;
    }
    .stChatInput input::placeholder {
        color: #6b6b80 !important;
    }
    .stChatInput button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 50% !important;
        padding: 6px 14px !important;
        color: white !important;
        border: none !important;
    }
    
    /* أزرار الفئات السريعة */
    .quick-buttons {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        justify-content: center;
        margin: 10px 0 20px 0;
        max-width: 760px;
        margin-left: auto;
        margin-right: auto;
    }
    .quick-buttons button {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
        color: #c0c0d0;
        padding: 8px 18px;
        border-radius: 30px;
        font-size: 13px;
        cursor: pointer;
        transition: 0.3s;
    }
    .quick-buttons button:hover {
        background: rgba(255,255,255,0.08);
        transform: translateY(-2px);
        border-color: #667eea;
    }
    
    /* مؤشر الكتابة */
    .typing-indicator {
        display: inline-block;
        background: #1e1e2a;
        padding: 10px 18px;
        border-radius: 18px;
        border-bottom-left-radius: 4px;
        border: 1px solid rgba(255,255,255,0.04);
    }
    .typing-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        margin: 0 3px;
        background: #667eea;
        border-radius: 50%;
        animation: pulse 1.4s infinite;
    }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
</style>
""", unsafe_allow_html=True)

# ─── الشريط العلوي ───
st.markdown("""
<div class="top-bar">
    <div class="brand">
        <span class="icon">⚡</span> نبراس X
    </div>
    <div class="status">
        <span class="dot"></span> متصل
    </div>
    <div class="actions">
        <button onclick="location.reload()">➕ جديد</button>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── دوال البحث ───
def search_web(query, max_results=5):
    """البحث في الويب باستخدام DuckDuckGo"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return None
        context = ""
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            body = r.get("body", "")
            url = r.get("href", r.get("url", ""))
            context += f"[{i}] {title}\n{body}\nالرابط: {url}\n\n"
        return context.strip()
    except Exception as e:
        return None

def get_current_events():
    """جلب الأحداث الجارية"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text("أحدث الأخبار والأحداث اليوم", max_results=3))
        if not results:
            return "لا توجد أحداث حالية."
        events = []
        for r in results[:3]:
            title = r.get("title", "")
            body = r.get("body", "")
            events.append(f"• {title}: {body[:150]}...")
        return "\n".join(events)
    except:
        return "تعذر جلب الأحداث."

# ─── تهيئة المحادثة ───
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_search" not in st.session_state:
    st.session_state.last_search = ""

# ─── عرض المحادثة ───
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">{msg["content"]}<span class="time-badge">{datetime.now().strftime("%I:%M %p")}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-bot">{msg["content"]}<span class="time-badge">{datetime.now().strftime("%I:%M %p")}</span></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─── أزرار سريعة ───
if not st.session_state.messages:
    st.markdown("""
    <div class="quick-buttons">
        <button onclick="document.querySelector('.stChatInput input').value='ما هي آخر الأخبار اليوم؟'; setTimeout(() => document.querySelector('.stChatInput button').click(), 200);">📰 الأخبار</button>
        <button onclick="document.querySelector('.stChatInput input').value='ما هي أهم الأحداث الرياضية اليوم؟'; setTimeout(() => document.querySelector('.stChatInput button').click(), 200);">⚽ رياضة</button>
        <button onclick="document.querySelector('.stChatInput input').value='ما هي آخر تطورات الذكاء الاصطناعي؟'; setTimeout(() => document.querySelector('.stChatInput button').click(), 200);">🤖 تقنية</button>
        <button onclick="document.querySelector('.stChatInput input').value='أخبرني عن الطقس اليوم'; setTimeout(() => document.querySelector('.stChatInput button').click(), 200);">🌤️ طقس</button>
        <button onclick="document.querySelector('.stChatInput input').value='ما هي آخر أخبار الاقتصاد؟'; setTimeout(() => document.querySelector('.stChatInput button').click(), 200);">📊 اقتصاد</button>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="max-width:760px; margin:0 auto 20px; display:flex; gap:8px; flex-wrap:wrap; justify-content:center;">
        <button onclick="document.querySelector('.stChatInput input').value='ما هي آخر الأحداث اليوم؟'; setTimeout(() => document.querySelector('.stChatInput button').click(), 200);" style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);color:#c0c0d0;padding:6px 14px;border-radius:30px;font-size:12px;cursor:pointer;">🔄 تحديث</button>
        <button onclick="document.querySelector('.stChatInput input').value='أعطني ملخصاً لأهم الأخبار'; setTimeout(() => document.querySelector('.stChatInput button').click(), 200);" style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);color:#c0c0d0;padding:6px 14px;border-radius:30px;font-size:12px;cursor:pointer;">📰 ملخص</button>
    </div>
    """, unsafe_allow_html=True)

# ─── مربع الإدخال ───
prompt = st.chat_input("اسأل نبراس عن أي شيء...", key="main_chat")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # مؤشر الكتابة
    with st.chat_message("assistant"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown("""
        <div class="typing-indicator">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            # ─── البحث في الويب ───
            search_results = search_web(prompt)
            
            # ─── تحضير التعليمات ───
            system_prompt = """أنت نبراس X، مساعد ذكي ومحدث.
            - تحدث بالعربية الفصحى أو العامية الخفيفة.
            - اعتمد على نتائج البحث للإجابة.
            - أذكر المصادر إذا توفرت.
            - اختصر الإجابة ولكن كن دقيقاً.
            - إذا كان السؤال عن الأحداث الجارية، استخدم المعلومات المحدثة.
            """
            
            if search_results:
                system_prompt += f"\n\n📌 معلومات محدثة من البحث:\n{search_results}"
            else:
                # إذا لم يجد نتائج، حاول جلب أحداث عامة
                events = get_current_events()
                system_prompt += f"\n\n📌 أحداث اليوم:\n{events}"
            
            # ─── طلب الرد ───
            messages = [
                {"role": "system", "content": system_prompt},
                *st.session_state.messages
            ]
            
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                stream=True,
                max_tokens=600
            )
            
            # إزالة مؤشر الكتابة
            typing_placeholder.empty()
            
            # كتابة الرد تدريجياً
            response = st.write_stream(stream)
            
            # حفظ الرد
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            typing_placeholder.empty()
            st.error(f"⚠️ خطأ: {str(e)}")
