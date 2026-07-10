import streamlit as st
from openai import OpenAI
import base64
from datetime import datetime
import re
import json
import os
from PIL import Image
import io

# ============================================================
# 1. إعدادات الصفحة
# ============================================================
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 2. المفتاح والعميل
# ============================================================
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير مضاف")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ============================================================
# 3. الذاكرة الدائمة
# ============================================================
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}]

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "sessions" not in st.session_state:
    st.session_state.sessions = []

memory = load_memory()

# ============================================================
# 4. CSS - واجهة أنيقة
# ============================================================
st.markdown("""
<style>
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background: #f7f7f8; }

    /* شريط علوي */
    .top-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(12px);
        padding: 6px 20px;
        border-bottom: 1px solid rgba(0,0,0,0.04);
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 1000;
        height: 44px;
    }
    .top-bar .icon { font-size: 16px; color: #1a1a1a; }
    .top-bar .actions { display: flex; gap: 4px; }
    .top-bar .actions button {
        background: transparent;
        border: none;
        cursor: pointer;
        font-size: 16px;
        padding: 4px 8px;
        border-radius: 50%;
        color: #444;
        transition: 0.2s;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .top-bar .actions button:hover { background: #f0f0f0; }

    /* منطقة المحادثة */
    .chat-container {
        max-width: 750px;
        margin: 60px auto 80px;
        padding: 0 20px;
    }

    /* رسائل */
    .msg-user {
        padding: 10px 16px;
        margin: 4px 0 8px auto;
        background: #e9ecef;
        border-radius: 18px;
        border-bottom-right-radius: 4px;
        max-width: 80%;
        width: fit-content;
        color: #1a1a1a;
        font-size: 15px;
        line-height: 1.6;
        clear: both;
    }
    .msg-bot {
        padding: 10px 16px;
        margin: 4px auto 8px 0;
        background: #ffffff;
        border-radius: 18px;
        border-bottom-left-radius: 4px;
        max-width: 80%;
        width: fit-content;
        color: #1a1a1a;
        font-size: 15px;
        line-height: 1.6;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        clear: both;
    }

    .chat-image {
        max-width: 250px;
        border-radius: 12px;
        margin: 6px 0;
        border: 1px solid #e5e5e5;
    }

    /* مربع الإدخال */
    .stChatInput {
        border-radius: 30px !important;
        border: 1px solid #e5e5e5 !important;
        background: #ffffff !important;
        padding: 2px 12px !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.02) !important;
    }
    .stChatInput input {
        border-radius: 30px !important;
        padding: 10px 16px !important;
        font-size: 15px !important;
        background: transparent !important;
    }
    .stChatInput button {
        background: #1a1a1a !important;
        border-radius: 50% !important;
        padding: 4px 10px !important;
        color: white !important;
        border: none !important;
    }

    /* تذييل */
    .footer {
        text-align: center;
        color: #aaa;
        font-size: 12px;
        padding: 16px 0 8px;
        border-top: 1px solid #f0f0f0;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 5. الشريط العلوي (أزرار تعمل)
# ============================================================
st.markdown("""
<div class="top-bar">
    <span class="icon">💬</span>
    <div class="actions">
        <button onclick="document.getElementById('menu').style.display='block'">☰</button>
        <button onclick="location.reload()">＋</button>
    </div>
</div>
<div id="menu" style="display:none; position:fixed; top:52px; left:16px; background:white; border-radius:14px; padding:6px; z-index:999; min-width:200px; box-shadow:0 8px 40px rgba(0,0,0,0.12); border:1px solid rgba(0,0,0,0.04);">
    <div style="padding:10px 14px; border-radius:10px; cursor:pointer; font-size:14px;" onclick="location.reload()">➕ محادثة جديدة</div>
    <div style="height:1px; background:#e5e5e5; margin:4px 10px;"></div>
    <div style="padding:10px 14px; border-radius:10px; cursor:pointer; font-size:14px;" onclick="document.getElementById('menu').style.display='none'">📋 المحادثات السابقة</div>
    <div style="height:1px; background:#e5e5e5; margin:4px 10px;"></div>
    <div style="padding:10px 14px; border-radius:10px; cursor:pointer; font-size:14px; color:#e74c3c;" onclick="document.getElementById('menu').style.display='none'">إغلاق</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 6. عرض المحادثة
# ============================================================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-bot">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 7. استخراج الاسم
# ============================================================
if st.session_state.user_name is None:
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_msg = st.session_state.messages[-1]["content"]
        match = re.search(r"اسمي\s+(\w+)", last_msg)
        if match:
            st.session_state.user_name = match.group(1)
            if st.session_state.user_name not in memory["users"]:
                memory["users"][st.session_state.user_name] = {"first_seen": datetime.now().isoformat()}
                save_memory(memory)
            st.session_state.messages.append(
                {"role": "assistant", "content": f"أهلاً {st.session_state.user_name}! سعيد برؤيتك 🤍"}
            )
            st.rerun()

# ============================================================
# 8. مربع الإدخال (صوت + صور)
# ============================================================
# العمود الأول: مربع الكتابة + زر الصوت
col1, col2 = st.columns([10, 1])

with col1:
    user_input = st.chat_input(
        "اكتب سؤالك... أو ارفع صورة",
        accept_file=True,
        file_type=["jpg", "jpeg", "png", "gif", "webp"]
    )

with col2:
    # زر الصوت داخل مربع الإدخال
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; height: 100%; padding-top: 8px;">
        <button id="audioBtn" style="
            background: transparent;
            border: none;
            font-size: 22px;
            cursor: pointer;
            color: #444;
            padding: 6px 10px;
            border-radius: 50%;
            transition: 0.2s;
        " onclick="toggleRecording()">🎤</button>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 9. معالجة الإدخال (نص + صور + بحث ويب + صوت)
# ============================================================
if user_input:
    query = user_input.text.strip() if hasattr(user_input, 'text') else str(user_input).strip()
    
    # معالجة الصور
    uploaded_images = []
    if hasattr(user_input, 'files') and user_input.files:
        for file in user_input.files:
            try:
                img_bytes = file.getvalue()
                img_b64 = base64.b64encode(img_bytes).decode()
                uploaded_images.append({
                    "name": file.name,
                    "data": img_b64
                })
            except:
                pass
    
    # بناء رسالة المستخدم
    user_message = query
    if uploaded_images:
        if query:
            user_message += f"\n📷 صورة: {uploaded_images[0]['name']}"
        else:
            user_message = f"📷 صورة: {uploaded_images[0]['name']}"
    
    if user_message.strip():
        st.session_state.messages.append({"role": "user", "content": user_message})
        
        with st.chat_message("user"):
            st.markdown(user_message)
        
        for img in uploaded_images:
            st.image(f"data:image/png;base64,{img['data']}", width=250)
        
        with st.chat_message("assistant"):
            with st.spinner("نبراس يفكر..."):
                try:
                    # بحث ويب محدث
                    search_results = ""
                    try:
                        search_response = client.responses.create(
                            model="gpt-4o-mini",
                            input=[{"role": "user", "content": f"ابحث عن: {query if query else 'وصف الصورة'}"}],
                            tools=[{"type": "web_search"}],
                            max_output_tokens=300
                        )
                        search_results = search_response.output_text
                    except:
                        pass
                    
                    system_prompt = f"""
                    أنت نبراس، صديق ذكي ودود.
                    - تحدث بأسلوب بسيط، بدون أيقونات.
                    - استخدم اسم المستخدم: {st.session_state.user_name if st.session_state.user_name else "لم أعرفه"}
                    - اعتمد على المعلومات التالية من البحث:
                    {search_results if search_results else "لا توجد نتائج بحث محدثة."}
                    """
                    
                    messages = [
                        {"role": "system", "content": system_prompt},
                        *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
                    ]
                    
                    if uploaded_images:
                        messages.append({
                            "role": "user",
                            "content": [
                                {"type": "text", "text": query or "صف هذه الصورة"},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{uploaded_images[0]['data']}"}}
                            ]
                        })
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=messages,
                            max_tokens=600
                        )
                    else:
                        messages.append({"role": "user", "content": query})
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=messages,
                            max_tokens=600
                        )
                    
                    answer = response.choices[0].message.content
                    
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.markdown(f'<div class="msg-bot">{answer}</div>', unsafe_allow_html=True)
                    
                    st.session_state.sessions.append({
                        "date": datetime.now().strftime("%H:%M - %d/%m"),
                        "messages": st.session_state.messages.copy()
                    })
                    
                    # تشغيل الصوت تلقائياً
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

# ============================================================
# 10. تذييل
# ============================================================
st.markdown("""
<div class="footer">
    نبراس · صديقك الذكي · 2026
</div>
""", unsafe_allow_html=True)
