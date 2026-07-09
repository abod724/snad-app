import streamlit as st
from openai import OpenAI
from ai import ask_ai
import base64
from datetime import datetime
import re
import json
import os

# -------------------------- إعدادات الصفحة --------------------------
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------- ملف الذاكرة الدائمة --------------------------
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

# -------------------------- ذاكرة الجلسة --------------------------
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "مرحبًا، أنا نبراس… ما هو اسمك؟"}]

if "all_chats" not in st.session_state:
    st.session_state.all_chats = []

memory = load_memory()

# -------------------------- المفتاح --------------------------
API_KEY = st.secrets.get("OPENAI_API_KEY")

if not API_KEY:
    st.error("🔴 المفتاح غير مضاف في إعدادات Streamlit")
    st.stop()

client = OpenAI(api_key=API_KEY)

# -------------------------- الشريط العلوي (نظيف) --------------------------
st.markdown("""
<style>
* {
    direction: rtl;
    text-align: right;
    font-family: 'Segoe UI', Tahoma, sans-serif;
}
.stApp {
    background: #ffffff;
    color: #1a1a1a;
}
#MainMenu, footer, header {visibility: hidden;}

/* شريط علوي نظيف */
.top-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: #ffffff;
    padding: 8px 20px;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    height: 50px;
}
.top-left {
    display: flex;
    align-items: center;
    gap: 12px;
}
.top-left button {
    background: none !important;
    border: none !important;
    font-size: 20px !important;
    padding: 4px 8px !important;
    cursor: pointer;
    color: #1a1a1a !important;
}
.top-left button:hover {
    background: #f3f4f6 !important;
    border-radius: 8px !important;
}
.top-right {
    display: flex;
    align-items: center;
    gap: 8px;
}
.top-right button {
    background: none !important;
    border: none !important;
    font-size: 20px !important;
    padding: 4px 8px !important;
    cursor: pointer;
    color: #1a1a1a !important;
}
.top-right button:hover {
    background: #f3f4f6 !important;
    border-radius: 8px !important;
}
.chat-area {
    max-width: 850px;
    margin: 70px auto 100px;
    padding: 0 20px;
}
.msg {
    padding: 12px 16px;
    margin: 8px 0;
    border-radius: 16px;
    max-width: 80%;
    line-height: 1.6;
    font-size: 15px;
}
.user {
    background: #1a1a1a;
    color: #ffffff;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}
.bot {
    background: #f3f4f6;
    color: #1a1a1a;
    margin-right: auto;
    border-bottom-left-radius: 4px;
}
div[data-testid="stChatInput"] {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    padding: 2px 12px !important;
}
div[data-testid="stChatInput"] input {
    color: #1a1a1a !important;
    font-weight: 500 !important;
    background: #ffffff !important;
}
div[data-testid="stChatInput"] button {
    background: #1a1a1a !important;
    color: #ffffff !important;
    border-radius: 50% !important;
}
/* إخفاء أيقونات Streamlit الزائدة */
.st-emotion-cache-1v0mbdj {
    display: none !important;
}
/* تنسيق المنسدلة */
div[data-testid="stPopover"] button {
    font-size: 20px !important;
    padding: 4px 8px !important;
    border-radius: 8px !important;
}
div[data-testid="stPopover"] button:hover {
    background: #f3f4f6 !important;
}
</style>
""", unsafe_allow_html=True)

# --- (شريط العلوي (نظيف)) ---
st.markdown('<div class="top-bar">', unsafe_allow_html=True)

# يسار: أيقونة المحادثات (⊕)
st.markdown(""" 
<div class="top-left">
    <button class="icon-btn" onclick="location.reload()" title="محادثة جديدة">⊕</button>
</div>
""", unsafe_allow_html=True)

# يمين: أيقونة القائمة المنسدلة (☰)
with st.container():
    col_right, _ = st.columns([0.1, 0.9])
    with col_right:
        with st.popover("☰"):
            st.markdown("### 📋 المحادثات السابقة")
            
            if st.button("➕ محادثة جديدة", use_container_width=True):
                st.session_state.chat_history = [{"role": "assistant", "content": "مرحباً، أنا نبراس"}]
                st.rerun()
            
            st.markdown("---")
            
            if "all_chats" in st.session_state and st.session_state.all_chats:
                for i, chat in enumerate(st.session_state.all_chats):
                    if st.button(f"💬 محادثة {i+1}", use_container_width=True):
                        st.session_state.chat_history = chat["messages"]
                        st.rerun()
            else:
                st.info("لا توجد محادثات سابقة")

st.markdown('</div>', unsafe_allow_html=True)
# -------------------------- عرض المحادثة --------------------------
st.markdown('<div class="chat-area">', unsafe_allow_html=True)

for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg bot">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- استخراج الاسم --------------------------
if st.session_state.user_name is None:
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
        last_msg = st.session_state.chat_history[-1]["content"]
        match = re.search(r"اسمي\s+(\w+)", last_msg)
        if match:
            st.session_state.user_name = match.group(1)
            if st.session_state.user_name not in memory["users"]:
                memory["users"][st.session_state.user_name] = {
                    "first_seen": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "interests": [],
                    "conversations": []
                }
            save_memory(memory)
            st.session_state.chat_history.append({"role": "assistant", "content": f"أهلاً بك {st.session_state.user_name}! أنا سعيد بلقائك 🤍"})
            st.rerun()

# -------------------------- مربع الكتابة (مع اسم نبراس) --------------------------
st.markdown("""
<div style="max-width: 850px; margin: 0 auto 10px; padding: 0 20px;">
    <div style="text-align: center; font-size: 13px; color: #9ca3af;">
        نبراس – صديقك الذكي
    </div>
</div>
""", unsafe_allow_html=True)

user_input = st.chat_input(
    "اكتب سؤالك هنا...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "pdf", "csv", "txt"],
    accept_audio=True
)

# -------------------------- معالجة الإدخال --------------------------
if user_input:
    query = user_input.text.strip() if hasattr(user_input, 'text') else str(user_input).strip()
    
    files_text = ""
    if hasattr(user_input, 'files') and user_input.files:
        for file in user_input.files:
            files_text += f"\n[ملف مرفوع: {file.name}]"
    
    full_query = query + files_text
    
    if full_query.strip():
        st.session_state.chat_history.append({"role": "user", "content": full_query})

        with st.spinner("🔍 جاري البحث..."):
            try:
                user_info = ""
                if st.session_state.user_name and st.session_state.user_name in memory["users"]:
                    user_data = memory["users"][st.session_state.user_name]
                    interests = user_data.get("interests", [])
                    if interests:
                        user_info = f"\n📌 اهتمامات المستخدم: {', '.join(interests)}"

                system_prompt = f"""
أنت نبراس، صديق ذكي تتحدث مع شخص تحبه.

🧠 **شخصيتك**:
- أنت صديق وليس برنامج أو موقع أخبار.
- اسم المستخدم هو: {st.session_state.user_name if st.session_state.user_name else "لم أعرفه بعد"}
{user_info}

🗣️ **أسلوبك**:
- تحدث كأنك جالس مع صديق.
- نادِ المستخدم باسمه.
- لا تستخدم كلمات رسمية.

🔥 **قاعدة مهمة**:
- ابحث في الويب عن إجابة سؤال المستخدم.
- لا تستخدم معرفتك القديمة (قبل 2025).
- لخص المعلومة بأسلوبك الخاص.
"""

if st.session_state.user_name and st.session_state.user_name in memory.get("users", {}):
    answer = ask_all(st.session_state.chat_history)
else:
    answer = "مرحباً! سجل اسمك للمتابعة."

st.session_state.chat_history.append({"role": "assistant", "content": answer})

user_key = st.session_state.user_name if st.session_state.user_name else "زائر"

if user_key in memory.get("users", {}):
    memory["users"][user_key]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    memory["users"][user_key]["conversations"].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": st.session_state.chat_history[-2:]
    })
else:
    memory["users"][user_key] = {
        "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "conversations": [{
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "messages": st.session_state.chat_history[-2:]
        }]
    }

save_memory(memory)

st.session_state.all_chats.append({
    "date": datetime.now().strftime("%Y:%M - %d/%m"),
    "messages": st.session_state.chat_history.copy(),
    "user_name": st.session_state.user_name if st.session_state.user_name else "زائر"
})
else:
    if st.session_state.user_name:
        # إنشاء مستخدم جديد
        memory["users"][st.session_state.user_name] = {
            "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "conversations": []
        }

save_memory(memory)

st.session_state.all_chats.append({
    "date": datetime.now().strftime("%Y:%M - %d/%m"),
    "messages": st.session_state.chat_history.copy(),
    "user_name": st.session_state.user_name
})
                try:
                    speech = client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=answer[:500],
                        response_format="mp3"
                    )
                    audio_b64 = base64.b64encode(speech.content).decode("utf-8")
                    st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")
                except Exception:
                    pass

                st.rerun()

            except Exception as e:
                st.error(f"❌ خطأ: {str(e)}")
