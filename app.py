import streamlit as st
from openai import OpenAI
import base64
from datetime import datetime
import re
import json
import os

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
# 4. CSS - واجهة أنيقة مثل ChatGPT
# ============================================================
st.markdown("""
<style>
    /* إخفاء عناصر Streamlit */
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background: #f7f7f8; }

    /* شريط علوي - بسيط ونظيف */
    .top-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(12px);
        padding: 6px 24px;
        border-bottom: 1px solid rgba(0,0,0,0.04);
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 1000;
        height: 48px;
    }
    .top-bar .brand {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 16px;
        font-weight: 500;
        color: #1a1a1a;
    }
    .top-bar .brand .icon {
        background: #1a1a1a;
        color: white;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
    }
    .top-bar .actions {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .top-bar .actions .btn-icon {
        background: transparent;
        border: none;
        cursor: pointer;
        font-size: 18px;
        padding: 6px 10px;
        border-radius: 30px;
        color: #444;
        transition: 0.2s;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .top-bar .actions .btn-icon:hover {
        background: #f0f0f0;
    }

    /* منطقة المحادثة */
    .chat-container {
        max-width: 750px;
        margin: 65px auto 80px;
        padding: 0 20px;
    }

    /* رسائل - فقاعات مثل ChatGPT */
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

    /* الصور في المحادثة */
    .chat-image {
        max-width: 250px;
        border-radius: 12px;
        margin: 6px 0;
        border: 1px solid #e5e5e5;
    }

    /* مربع الإدخال - مثل ChatGPT (ثابت في الأسفل) */
    .stChatInput {
        border-radius: 30px !important;
        border: 1px solid #e5e5e5 !important;
        background: #ffffff !important;
        padding: 2px 12px !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.02) !important;
        position: fixed !important;
        bottom: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 750px !important;
        max-width: 92% !important;
        z-index: 999 !important;
    }
    .stChatInput input {
        border-radius: 30px !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
        background: transparent !important;
    }
    .stChatInput button {
        background: #1a1a1a !important;
        border-radius: 50% !important;
        padding: 4px 12px !important;
        color: white !important;
        border: none !important;
    }

    /* تذييل */
    .footer {
        text-align: center;
        color: #aaa;
        font-size: 12px;
        padding: 16px 0 90px;
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
    <div class="brand">
        <span class="icon">💬</span> نبراس
    </div>
    <div class="actions">
        <button class="btn-icon" id="menuBtn">☰</button>
        <button class="btn-icon" id="newChatBtn">＋</button>
    </div>
</div>
""", unsafe_allow_html=True)

# أزرار الشريط العلوي عبر أعمدة (تعمل فعلاً)
col1, col2, col3 = st.columns([1, 10, 1])
with col1:
    with st.popover("☰"):
        st.markdown("### 📋 المحادثات")
        if st.button("➕ محادثة جديدة", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}]
            st.rerun()
        st.markdown("---")
        if st.session_state.sessions:
            for i, s in enumerate(st.session_state.sessions[::-1]):
                if st.button(f"💬 {s['date']}", key=f"pop_{i}", use_container_width=True):
                    st.session_state.messages = s["messages"]
                    st.rerun()
        else:
            st.info("لا توجد محادثات سابقة")
with col3:
    if st.button("➕", key="new_chat_header"):
        st.session_state.messages = [{"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}]
        st.rerun()

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
# 8. مربع الإدخال (مع زر صوت داخلي)
# ============================================================
# عمودان: الأول لمربع الكتابة، الثاني لزر الصوت
col_input, col_audio = st.columns([12, 1])

with col_input:
    user_input = st.chat_input(
        "اكتب سؤالك... أو ارفع صورة",
        accept_file=True,
        file_type=["jpg", "jpeg", "png", "gif", "webp"]
    )

with col_audio:
    # زر الصوت داخل مربع الإدخال
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; height: 100%; padding-top: 6px;">
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
# 9. معالجة الإدخال (نص + صور + بحث + صوت)
# ============================================================
if user_input:
    query = user_input.text.strip() if hasattr(user_input, 'text') else str(user_input).strip()
    
    # معالجة الصور المرفوعة
    uploaded_images = []
    if hasattr(user_input, 'files') and user_input.files:
        for file in user_input.files:
            try:
                img_bytes = file.getvalue()
                img_b64 = base64.b64encode(img_bytes).decode()
                uploaded_images.append({"name": file.name, "data": img_b64})
            except:
                pass
    
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

# ============================================================
# 11. كود جافا سكريبت لتسجيل الصوت (يعمل داخل المتصفح)
# ============================================================
st.components.v1.html("""
<script>
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

function toggleRecording() {
    const btn = document.getElementById('audioBtn');
    
    if (isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        btn.textContent = '🎤';
        btn.style.color = '#444';
        return;
    }
    
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const reader = new FileReader();
                reader.onload = function(e) {
                    const base64Audio = e.target.result.split(',')[1];
                    // إرسال الصوت إلى الخادم (يمكنك ربطه بـ API تحويل الصوت إلى نص)
                    // هنا نضع الكود المطلوب لإرسال الصوت
                    alert('تم تسجيل الصوت، سيتم إرساله قريباً');
                };
                reader.readAsDataURL(audioBlob);
                btn.textContent = '🎤';
                btn.style.color = '#444';
                isRecording = false;
            };
            
            mediaRecorder.start();
            isRecording = true;
            btn.textContent = '⏹️';
            btn.style.color = '#e74c3c';
        })
        .catch(() => {
            alert('الرجاء السماح بالوصول إلى المايكروفون');
        });
}
</script>
""", height=0)
