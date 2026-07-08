import streamlit as st
from openai import OpenAI
import base64
from datetime import datetime
import re

# -------------------------- إعدادات الصفحة --------------------------
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------- ذاكرة المستخدم --------------------------
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "مرحبًا، أنا نبراس… ما هو اسمك؟"}]

if "all_chats" not in st.session_state:
    st.session_state.all_chats = []

# -------------------------- المفتاح --------------------------
API_KEY = st.secrets.get("OPENAI_API_KEY")

if not API_KEY:
    st.error("🔴 المفتاح غير مضاف في إعدادات Streamlit")
    st.stop()

client = OpenAI(api_key=API_KEY)

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
    padding: 8px 15px;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.chat-area {
    max-width: 850px;
    margin: 70px auto 100px;
}
.msg {
    padding: 12px 16px;
    margin: 6px 0;
    border-radius: 16px;
    max-width: 80%;
}
.user {
    background: #1a1a1a;
    color: #ffffff;
    margin-left: auto;
}
.bot {
    background: #f3f4f6;
    color: #1a1a1a;
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
div[data-testid="stPopover"] button {
    font-size: 18px !important;
    padding: 4px 10px !important;
    border-radius: 8px !important;
}
div[data-testid="stPopover"] button:hover {
    background: #f3f4f6 !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------- الشريط العلوي --------------------------
st.markdown('<div class="top-bar">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([0.5, 5, 0.8])

with col1:
    if st.button("✏️ جديد", key="new_chat_btn", help="بدء محادثة جديدة"):
        user_name = st.session_state.user_name if st.session_state.user_name else ""
        st.session_state.chat_history = [{"role": "assistant", "content": f"مرحبًا بعودتك {user_name}… كيف أقدر أساعدك اليوم؟"}]
        st.rerun()

with col2:
    st.markdown(
        """
        <div style="display: flex; justify-content: center; align-items: center; gap: 8px;">
            <span style="font-size: 20px; color: #dc2626;">❤️</span>
            <span style="font-size: 20px; font-weight: 700; color: #1a1a1a;">نبراس</span>
            <span style="font-size: 13px; color: #6b7280;">– صديقك الذكي</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    with st.popover("📋"):
        if st.session_state.all_chats:
            for i, c in enumerate(st.session_state.all_chats):
                if st.button(f"محادثة {i+1} - {c['date']}", use_container_width=True, key=f"chat_{i}"):
                    st.session_state.chat_history = c["messages"]
                    st.session_state.user_name = c.get("user_name", st.session_state.user_name)
                    st.rerun()
        else:
            st.info("ما فيه محادثات")

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
            st.session_state.chat_history.append({"role": "assistant", "content": f"أهلاً بك {st.session_state.user_name}! كيف أقدر أساعدك اليوم؟"})
            st.rerun()

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
    
    files_text = ""
    if hasattr(user_input, 'files') and user_input.files:
        for file in user_input.files:
            files_text += f"\n[ملف مرفوع: {file.name}]"
    
    full_query = query + files_text
    
    if full_query.strip():
        st.session_state.chat_history.append({"role": "user", "content": full_query})

        with st.spinner("🔍 جاري البحث..."):
            try:
                system_prompt = f"""
أنت نبراس، صديق ذكي تتحدث مع شخص تحبه.

🧠 **شخصيتك**:
- أنت صديق وليس برنامج أو موقع أخبار.
- اسم المستخدم هو: {st.session_state.user_name if st.session_state.user_name else "لم أعرفه بعد"}

🗣️ **أسلوبك**:
- تحدث كأنك جالس مع صديق.
- نادِ المستخدم باسمه.
- لا تستخدم كلمات رسمية.

🔥 **قاعدة مهمة**:
- ابحث في الويب عن إجابة سؤال المستخدم.
- لا تستخدم معرفتك القديمة (قبل 2025).
"""

                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=[
                        {"role": "system", "content": system_prompt},
                        *st.session_state.chat_history
                    ],
                    tools=[{"type": "web_search"}],
                    max_output_tokens=600,
                )

                answer = response.output_text

                st.session_state.chat_history.append({"role": "assistant", "content": answer})

                st.session_state.all_chats.append({
                    "date": datetime.now().strftime("%H:%M - %d/%m"),
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
