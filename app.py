import streamlit as st
from openai import OpenAI
import base64
from datetime import datetime
import re
import json
import os
import time
from PIL import Image
import io

# ============================================
# 1. إعدادات الصفحة
# ============================================
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# 2. المفتاح
# ============================================
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير مضاف")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ============================================
# 3. الذاكرة
# ============================================
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "مرحباً، أنا نبراس"}]  # بدون أيقونة

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "all_sessions" not in st.session_state:
    st.session_state.all_sessions = []

memory = load_memory()

# ============================================
# 4. CSS (واجهة نظيفة)
# ============================================
st.markdown("""
<style>
    /* إخفاء عناصر Streamlit */
    #MainMenu, footer, header { visibility: hidden; }
    
    /* خلفية الصفحة */
    .stApp {
        background: #f7f7f8;
    }
    
    /* شريط علوي */
    .top-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: #ffffff;
        padding: 10px 20px;
        border-bottom: 1px solid #e5e5e5;
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 1000;
        height: 50px;
    }
    .top-bar .brand {
        font-size: 18px;
        font-weight: 600;
        color: #1a1a1a;
    }
    .top-bar button {
        background: transparent;
        border: none;
        font-size: 16px;
        cursor: pointer;
        padding: 6px 12px;
        border-radius: 8px;
        color: #333;
    }
    .top-bar button:hover {
        background: #f0f0f0;
    }
    
    /* منطقة المحادثة */
    .chat-area {
        max-width: 750px;
        margin: 70px auto 100px;
        padding: 0 20px;
    }
    
    /* رسائل بدون أيقونات */
    .msg-user {
        text-align: left;
        padding: 10px 16px;
        margin: 8px 0;
        background: #e9ecef;
        border-radius: 18px;
        border-bottom-right-radius: 4px;
        max-width: 80%;
        float: right;
        clear: both;
        color: #1a1a1a;
        font-size: 15px;
        line-height: 1.6;
    }
    .msg-bot {
        text-align: left;
        padding: 10px 16px;
        margin: 8px 0;
        background: #ffffff;
        border-radius: 18px;
        border-bottom-left-radius: 4px;
        max-width: 80%;
        float: left;
        clear: both;
        color: #1a1a1a;
        font-size: 15px;
        line-height: 1.6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* الصور في المحادثة */
    .chat-image {
        max-width: 300px;
        border-radius: 12px;
        margin: 6px 0;
        border: 1px solid #e5e5e5;
    }
    
    /* مربع الإدخال */
    .stChatInput {
        border-radius: 30px !important;
        border: 1px solid #e5e5e5 !important;
        background: #ffffff !important;
        padding: 4px 16px !important;
    }
    .stChatInput input {
        border-radius: 30px !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
    }
    .stChatInput button {
        background: #1a1a1a !important;
        border-radius: 50% !important;
        padding: 6px 10px !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# 5. الشريط العلوي
# ============================================
st.markdown("""
<div class="top-bar">
    <span class="brand">💬 نبراس</span>
    <div>
        <button onclick="location.reload()">➕ جديد</button>
        <button onclick="document.getElementById('menu').style.display='block'">📋</button>
    </div>
</div>
<!-- قائمة المحادثات السابقة -->
<div id="menu" style="display:none; position:fixed; top:55px; right:20px; background:white; border:1px solid #e5e5e5; border-radius:12px; padding:12px; z-index:1001; min-width:200px; box-shadow:0 4px 20px rgba(0,0,0,0.08);">
    <div style="font-weight:600; margin-bottom:8px;">📋 المحادثات</div>
    <div id="chat-list"></div>
    <button onclick="document.getElementById('menu').style.display='none'" style="margin-top:8px; background:#f0f0f0; border:none; border-radius:8px; padding:6px 12px; width:100%; cursor:pointer;">إغلاق</button>
</div>
""", unsafe_allow_html=True)

# قائمة المحادثات (من خلال ستريمليت)
with st.sidebar:
    st.markdown("### 📋 المحادثات")
    if st.button("➕ محادثة جديدة", use_container_width=True):
        st.session_state.chat_history = [{"role": "assistant", "content": "مرحباً، أنا نبراس"}]
        st.rerun()
    st.markdown("---")
    if st.session_state.all_sessions:
        for i, s in enumerate(st.session_state.all_sessions[::-1]):
            if st.button(f"💬 {s['date']}", key=f"side_{i}", use_container_width=True):
                st.session_state.chat_history = s["messages"]
                st.rerun()
    else:
        st.info("لا توجد محادثات سابقة")
st.sidebar.empty()  # لإخفاء الشريط الجانبي (يبقى فقط للقائمة)

# ============================================
# 6. عرض المحادثة (بدون أيقونات)
# ============================================
st.markdown('<div class="chat-area">', unsafe_allow_html=True)

for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-bot">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# 7. استخراج الاسم
# ============================================
if st.session_state.user_name is None:
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
        last_msg = st.session_state.chat_history[-1]["content"]
        match = re.search(r"اسمي\s+(\w+)", last_msg)
        if match:
            st.session_state.user_name = match.group(1)
            if st.session_state.user_name not in memory["users"]:
                memory["users"][st.session_state.user_name] = {
                    "first_seen": datetime.now().isoformat()
                }
                save_memory(memory)
            st.session_state.chat_history.append(
                {"role": "assistant", "content": f"أهلاً {st.session_state.user_name}! سعيد بلقائك 🤍"}
            )
            st.rerun()

# ============================================
# 8. مربع الإدخال (مع رفع الصور)
# ============================================
user_input = st.chat_input(
    "اكتب سؤالك... أو ارفع صورة",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"]
)

# ============================================
# 9. معالجة الإدخال
# ============================================
if user_input:
    query = user_input.text.strip() if hasattr(user_input, 'text') else str(user_input).strip()
    
    # معالجة الصور
    images_data = []
    if hasattr(user_input, 'files') and user_input.files:
        for file in user_input.files:
            try:
                img_bytes = file.getvalue()
                img_b64 = base64.b64encode(img_bytes).decode()
                images_data.append({
                    "name": file.name,
                    "data": img_b64
                })
            except:
                pass
    
    if query or images_data:
        # بناء رسالة المستخدم
        user_message = query
        if images_data:
            if query:
                user_message += "\n\n"
            user_message += f"📷 صورة: {images_data[0]['name']}"
        
        # إضافة للمحادثة
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        
        # عرض رسالة المستخدم
        st.markdown(f'<div class="msg-user">{user_message}</div>', unsafe_allow_html=True)
        
        # عرض الصورة
        for img in images_data:
            st.markdown(f'<img src="data:image/png;base64,{img["data"]}" class="chat-image" />', unsafe_allow_html=True)
        
        # مؤشر التفكير
        with st.spinner("نبراس يفكر..."):
            try:
                system_prompt = f"""
                أنت نبراس، صديق ذكي ودود.
                - تحدث بأسلوب بسيط وطبيعي، بدون أيقونات.
                - إذا أرسل المستخدم صورة، صفها بأسلوبك.
                - استخدم اسم المستخدم إذا عرفته: {st.session_state.user_name if st.session_state.user_name else "لم أعرفه"}
                - اختصر الإجابة ولا تبالغ في الإطالة.
                """
                
                # إرسال الطلب (مع دعم الصور في حال وجودها)
                messages = [
                    {"role": "system", "content": system_prompt},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history[:-1]],
                    {"role": "user", "content": query or "أخبرني عن هذه الصورة"}
                ]
                
                # إذا كانت هناك صور، نضيفها بطريقة مختلفة
                if images_data:
                    # نستخدم الـ Vision API
                    vision_messages = [
                        {"role": "system", "content": system_prompt},
                        *[{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history[:-1]]
                    ]
                    # إضافة الصورة كـ content مع نوع image_url
                    vision_messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": query or "صف هذه الصورة"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{images_data[0]['data']}"}}
                        ]
                    })
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=vision_messages,
                        max_tokens=600
                    )
                else:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        max_tokens=600
                    )
                
                answer = response.choices[0].message.content
                
                # إضافة الرد للمحادثة
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                
                # عرض الرد
                st.markdown(f'<div class="msg-bot">{answer}</div>', unsafe_allow_html=True)
                
                # حفظ الجلسة
                st.session_state.all_sessions.append({
                    "date": datetime.now().strftime("%H:%M - %d/%m"),
                    "messages": st.session_state.chat_history.copy()
                })
                
                # صوت
                try:
                    speech = client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=answer[:300],
                        response_format="mp3"
                    )
                    audio_b64 = base64.b64encode(speech.content).decode("utf-8")
                    st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")
                except:
                    pass
                
                st.rerun()
                
            except Exception as e:
                st.error(f"⚠️ خطأ: {str(e)}")
