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
    initial_sidebar_state="expanded"
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
# 4. الشريط الجانبي (القائمة والمحادثات والصوت)
# ============================================================
with st.sidebar:
    st.markdown("## 💬 نبراس")
    st.markdown("---")
    
    if st.button("➕ محادثة جديدة", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}]
        st.rerun()
    
    st.markdown("### 📋 المحادثات السابقة")
    if st.session_state.sessions:
        for i, s in enumerate(st.session_state.sessions[::-1]):
            if st.button(f"💬 {s['date']}", key=f"side_{i}", use_container_width=True):
                st.session_state.messages = s["messages"]
                st.rerun()
    else:
        st.info("لا توجد محادثات سابقة")
    
    st.markdown("---")
    st.markdown("### 🎤 الصوت")
    if st.button("🎤 اضغط للتحدث", use_container_width=True):
        st.warning("سيتم إضافة التسجيل الصوتي قريباً")

# ============================================================
# 5. واجهة المحادثة
# ============================================================
st.markdown("""
<style>
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background: #f7f7f8; }
    .chat-container {
        max-width: 750px;
        margin: 20px auto 60px;
        padding: 0 20px;
    }
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
# 8. مربع الإدخال
# ============================================================
user_input = st.chat_input(
    "اكتب سؤالك... أو ارفع صورة",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "gif", "webp"]
)

# ============================================================
# 9. معالجة الإدخال
# ============================================================
if user_input:
    query = user_input.text.strip() if hasattr(user_input, 'text') else str(user_input).strip()
    
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
