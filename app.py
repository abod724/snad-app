import streamlit as st
from openai import OpenAI
import base64
from datetime import datetime
from serpapi import GoogleSearch
import json
import os

# -------------------------- إعدادات الصفحة --------------------------
st.set_page_config(
    page_title="Nbras",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------- المفاتيح --------------------------
API_KEY = st.secrets.get("OPENAI_API_KEY")
SERPAPI_API_KEY = st.secrets.get("SERPAPI_API_KEY")

if not API_KEY:
    st.error("⚠️ API key not found")
    st.stop()

client = OpenAI(api_key=API_KEY)

# -------------------------- الذاكرة (Memory) --------------------------
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

if "memory" not in st.session_state:
    st.session_state.memory = load_memory()

user_id = "default_user"

if user_id not in st.session_state.memory:
    st.session_state.memory[user_id] = []

if "chat_history" not in st.session_state:
    if st.session_state.memory[user_id]:
        st.session_state.chat_history = st.session_state.memory[user_id]
    else:
        st.session_state.chat_history = [{"role": "assistant", "content": "مرحبًا، أنا نبراس… كيف أقدر أساعدك اليوم؟"}]

# -------------------------- دالة البحث --------------------------
def search_google(query):
    if not SERPAPI_API_KEY:
        return ""
    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "num": 3
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        
        snippets = []
        if "organic_results" in results:
            for result in results["organic_results"][:3]:
                snippet = result.get("snippet", "")
                if snippet:
                    snippets.append(snippet)
        
        if snippets:
            return "\n".join(snippets)
        return ""
    except:
        return ""

# -------------------------- CSS --------------------------
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

.top-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: #ffffff;
    padding: 12px 25px;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.chat-area {
    max-width: 850px;
    margin: 80px auto 120px;
    padding: 10px 5px 30px;
}

.msg {
    padding: 12px 16px;
    margin: 6px 0;
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
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    margin-bottom: 10px !important;
}

div[data-testid="stChatInput"] input {
    color: #1a1a1a !important;
    font-weight: 500 !important;
    background: #ffffff !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    font-size: 15px !important;
}

div[data-testid="stChatInput"] input::placeholder {
    color: #9ca3af !important;
}

div[data-testid="stChatInput"] button {
    background: #1a1a1a !important;
    color: #ffffff !important;
    border-radius: 50% !important;
    padding: 6px !important;
}

div[data-testid="stPopover"] {
    border-radius: 12px !important;
    border: 1px solid #e5e7eb !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
    padding: 8px !important;
}

div[data-testid="stPopover"] button {
    border-bottom: none !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    margin: 2px 0 !important;
    font-size: 14px !important;
}

div[data-testid="stPopover"] button:hover {
    background: #f3f4f6 !important;
}

.stProgress > div > div {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------- الشريط العلوي --------------------------
st.markdown('<div class="top-bar">', unsafe_allow_html=True)

col_left, col_center, col_right = st.columns([1.2, 2, 1.2])

with col_left:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0;">
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 8px 16px 8px 14px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        ">
            <span style="font-size: 22px; color: white; transform: rotate(-10deg);">✍️</span>
            <span style="font-size: 20px; font-weight: 700; color: white; letter-spacing: 0.5px;">Nbras</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_center:
    st.markdown(
        """
        <div style="text-align: center;">
            <p style="margin: 0; font-size: 13px; color: #6b7280;">مساعدك الذكي – بسيط، سريع، واضح</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_right:
    with st.popover("📋 المحادثات السابقة"):
        if st.button("🗑️ مسح الذاكرة", use_container_width=True):
            st.session_state.memory[user_id] = []
            st.session_state.chat_history = [{"role": "assistant", "content": "مرحبًا، أنا نبراس… كيف أقدر أساعدك اليوم؟"}]
            save_memory(st.session_state.memory)
            st.rerun()
        st.divider()
        if "all_chats" not in st.session_state:
            st.session_state.all_chats = []
        if st.session_state.all_chats:
            for i, c in enumerate(st.session_state.all_chats[-5:]):
                if st.button(f"📝 محادثة {i+1} - {c['date']}", use_container_width=True):
                    st.session_state.chat_history = c["messages"]
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

# -------------------------- مربع الكتابة --------------------------
user_input = st.chat_input(
    "اكتب سؤالك هنا...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "pdf", "csv", "txt"],
    accept_audio=True
)

# -------------------------- معالجة الإدخال --------------------------
if user_input:
    query = user_input.text.strip() if hasattr(user_input, 'text') else str(user_input).strip()
    
    if query:
        st.session_state.chat_history.append({"role": "user", "content": query})
        
        st.session_state.memory[user_id] = st.session_state.chat_history
        save_memory(st.session_state.memory)

        with st.spinner("⏳ جاري التفكير..."):
            try:
                search_results = search_google(query)
                
                system_prompt = f"""
أنت «نبراس» – مساعد ذكي، سريع، وأسلوبك بسيط وواضح.
تتحدث بالعربية الفصحى.

🎯 دورك:
- الإجابة عن الأسئلة العامة، التقنية، اليومية.
- استخدم نقاطاً مختصرة.
- اجعل الإجابة مباشرة.

📌 معلومات من البحث:
{search_results if search_results else "لا توجد معلومات بحث محدثة."}
"""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *st.session_state.chat_history
                    ],
                    max_tokens=500,
                    temperature=0.7
                )

                answer = response.choices[0].message.content

                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                
                st.session_state.memory[user_id] = st.session_state.chat_history
                save_memory(st.session_state.memory)

                if "all_chats" not in st.session_state:
                    st.session_state.all_chats = []
                st.session_state.all_chats.append({
                    "date": datetime.now().strftime("%H:%M - %d/%m"),
                    "messages": st.session_state.chat_history.copy()
                })

                try:
                    speech = client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=answer,
                        response_format="mp3"
                    )
                    audio_b64 = base64.b64encode(speech.content).decode("utf-8")
                    st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")
                except:
                    pass

                st.rerun()

            except Exception as e:
                st.error(f"❌ خطأ: {str(e)}")
