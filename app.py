import streamlit as st
from openai import OpenAI
import base64
from datetime import datetime

# -------------------------- إعدادات الصفحة --------------------------
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------- قراءة المفتاح الآمنة --------------------------
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("⚠️ المفتاح غير مضاف في الإعدادات")
    st.stop()

client = OpenAI(api_key=API_KEY)

# -------------------------- تصميم الواجهة حسب طلبك --------------------------
st.markdown("""
<style>
* {direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, sans-serif;}
.stApp {background: #f8fafc; color: #1e293b;}
#MainMenu, footer, header {visibility: hidden;}

/* شريط الأعلى */
.top-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: white;
    padding: 12px 20px;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
}
.top-left {display: flex; gap: 10px; align-items: center;}
.top-center h1 {margin: 0; font-size: 28px; color: #165DFF;}

/* منطقة المحادثة */
.chat-area {
    max-width: 900px;
    margin: 70px auto 120px;
    padding: 20px;
}
.msg {
    padding: 14px 18px;
    margin: 12px 0;
    border-radius: 20px;
    max-width: 80%;
    line-height: 1.6;
}
.user {background: #165DFF; color: white; margin-left: auto; border-bottom-right-radius: 6px;}
.bot {background: white; border: 1px solid #e2e8f0; margin-right: auto; border-bottom-left-radius: 6px;}

/* مربع الكتابة الدائري */
.input-box {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 90%;
    max-width: 900px;
    background: white;
    border-radius: 50px;
    padding: 12px 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    display: flex;
    align-items: center;
    gap: 12px;
    z-index: 999;
}
.input-box input {
    flex: 1;
    border: none;
    outline: none;
    font-size: 16px;
    padding: 8px;
}
.circle-btn {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}
.voice-btn {background: #10B981; color: white;}
.send-btn {background: #165DFF; color: white;}
</style>
""", unsafe_allow_html=True)

# -------------------------- شريط الأعلى --------------------------
st.markdown('<div class="top-bar">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1,2,1])
with col1:
    if st.button("✏️ جديد", help="بدء محادثة جديدة"):
        st.session_state.chat_history = [{"role": "assistant", "content": "تحدث مع نبراس"}]
        st.rerun()
    st.button("⋮⋮⋮", help="خيارات إضافية")
with col2:
    st.markdown("<h1>نبراس</h1>", unsafe_allow_html=True)
with col3:
    with st.popover("📋 المحادثات السابقة"):
        if "all_chats" not in st.session_state:
            st.session_state.all_chats = []
        if st.session_state.all_chats:
            for i, c in enumerate(st.session_state.all_chats):
                if st.button(f"محادثة {i+1} - {c['date']}", use_container_width=True):
                    st.session_state.chat_history = c["messages"]
                    st.rerun()
        else:
            st.info("لا توجد محادثات سابقة")
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- سجل المحادثة --------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "تحدث مع نبراس"}]

st.markdown('<div class="chat-area">', unsafe_allow_html=True)
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg bot">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- مربع الكتابة الدائري --------------------------
st.markdown('<div class="input-box">', unsafe_allow_html=True)
voice_input = st.audio_input("🎤", label_visibility="collapsed")
user_input = st.text_input("", placeholder="اكتب هنا...", label_visibility="collapsed")
send = st.button("📤", type="primary")
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- معالجة الصوت --------------------------
if voice_input:
    with st.spinner("جاري تحويل الصوت..."):
        try:
            res = client.audio.transcriptions.create(model="whisper-1", file=voice_input, language="ar")
            user_input = res.text
        except Exception as e:
            st.error(f"خطأ: {str(e)}")

# -------------------------- إرسال السؤال وجلب الرد --------------------------
if (send or user_input) and user_input.strip():
    st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
    
    with st.spinner("نبراس يفكر..."):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "أنت نبراس، أجب بإيجاز شديد، لا تطل الكلام، لا توجه لمصادر خارجية، تحدث بالعربية الواضحة."},
                    *st.session_state.chat_history
                ],
                temperature=0.4,
                max_tokens=300
            )
            answer = response.choices[0].message.content
            st.session_state.chat_history.append({"role": "assistant", "content": answer})

            # حفظ المحادثة السابقة
            if "all_chats" not in st.session_state:
                st.session_state.all_chats = []
            st.session_state.all_chats.append({
                "date": datetime.now().strftime("%H:%M"),
                "messages": st.session_state.chat_history.copy()
            })

            # تحويل الرد لصوت
            speech = client.audio.speech.create(model="tts-1", voice="alloy", input=answer)
            audio_b64 = base64.b64encode(speech.content).decode("utf-8")
            st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")

            st.rerun()
        except Exception as e:
            st.error(f"خطأ: {str(e)}")
