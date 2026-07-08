import streamlit as st
from openai import OpenAI
import os
from datetime import datetime
from dotenv import load_dotenv
import requests
import json

# ============================
#  تحميل المفاتيح
# ============================
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

# ============================
#  إعدادات الصفحة
# ============================
st.set_page_config(page_title="نبراس", page_icon="✍️", layout="wide")

# ============================
#  التحقق من المفاتيح
# ============================
if not OPENAI_API_KEY:
    st.error("⚠️ مفتاح OpenAI غير موجود. أضفه في ملف .env")
    st.stop()

try:
    client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    st.error(f"⚠️ خطأ في مفتاح OpenAI: {e}")
    st.stop()

# ============================
#  ملف الذاكرة
# ============================
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_memory(data):
    try:
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

if "memory" not in st.session_state:
    st.session_state.memory = load_memory()

user_id = "default_user"

if user_id not in st.session_state.memory:
    st.session_state.memory[user_id] = []

if "messages" not in st.session_state:
    if st.session_state.memory[user_id]:
        st.session_state.messages = st.session_state.memory[user_id]
    else:
        st.session_state.messages = [{"role": "assistant", "content": "مرحباً، أنا نبراس"}]

def save_current_memory():
    st.session_state.memory[user_id] = st.session_state.messages
    save_memory(st.session_state.memory)

# ============================
#  دالة البحث في الويب
# ============================
def search_web(query):
    """البحث في قوقل عبر Google Custom Search"""
    if not GOOGLE_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
        return ""
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_SEARCH_ENGINE_ID,
        "q": query,
        "num": 2
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if "items" in data:
            results = []
            for item in data["items"][:2]:
                snippet = item.get("snippet", "")
                if snippet:
                    results.append(snippet)
            return "\n".join(results) if results else ""
        return ""
    except Exception as e:
        return ""

# ============================
#  CSS للواجهة
# ============================
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}

.top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 20px;
    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
}

.icon-btn {
    background: transparent !important;
    border: none !important;
    padding: 4px 6px !important;
    font-size: 20px !important;
    cursor: pointer;
    color: #1a1a1a;
}

.chat-container {
    margin-top: 65px;
    padding: 10px 20px;
    max-width: 850px;
    margin-left: auto;
    margin-right: auto;
}
</style>
""", unsafe_allow_html=True)

# ============================
#  الشريط العلوي
# ============================
st.markdown("""
<div class="top-bar">
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 18px;">●</span>
        <span style="font-size: 20px; font-weight: 700; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">نبراس</span>
        <span style="font-size: 12px; color: #6b7280;">- صديقك الذكي</span>
    </div>
    <div>
        <span class="icon-btn">☰</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================
#  عرض المحادثة
# ============================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

st.markdown('</div>', unsafe_allow_html=True)

# ============================
#  مربع الكتابة
# ============================
prompt = st.chat_input("اكتب سؤالك هنا...")

if prompt:
    # إضافة سؤال المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_current_memory()
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # البحث في الويب
    with st.spinner("🔍 نبراس يبحث..."):
        search_results = search_web(prompt)
    
    # رد نبراس
    system_prompt = f"""
    أنت نبراس، مساعد ذكي ومختصر.
    استخدم المعلومات التالية للإجابة على سؤال المستخدم:
    
    {search_results if search_results else "لا توجد معلومات محدثة من البحث."}
    
    إذا كانت المعلومات غير كافية، استخدم معرفتك العامة.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                *st.session_state.messages
            ],
            max_tokens=300
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"⚠️ حدث خطأ: {str(e)}"
    
    # إضافة رد نبراس
    st.session_state.messages.append({"role": "assistant", "content": answer})
    save_current_memory()
    
    with st.chat_message("assistant"):
        st.write(answer)
    
    st.rerun()
