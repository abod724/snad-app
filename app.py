RELOAD = "force_rebuild_v1"
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
    st.error("⚠️ المفتاح غير مضاف في إعدادات Streamlit")
    st.stop()

client = OpenAI(api_key=API_KEY)

# -------------------------- تصميم واجهة فاخرة (أسود + ذهبي + أزرق) --------------------------
st.markdown("""
<style>
* {
    direction: rtl;
    text-align: right;
    font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif;
}
.stApp {
    background: radial-gradient(circle at top, #0f172a 0%, #020617 45%, #000000 100%);
    color: #e5e7eb;
}
#MainMenu, footer, header {visibility: hidden;}

/* شريط الأعلى الفاخر */
.top-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: linear-gradient(90deg, #020617, #0f172a, #1d4ed8);
    padding: 14px 25px;
    border-bottom: 1px solid rgba(148,163,184,0.35);
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
    box-shadow: 0 4px 18px rgba(15,23,42,0.8);
}
.top-left {
    display: flex;
    gap: 10px;
    align-items: center;
}
.top-left button {
    border-radius: 999px !important;
}
.top-center h1 {
    margin: 0;
    font-size: 30px;
    font-weight: 800;
    background: linear-gradient(90deg, #facc15, #38bdf8, #f97316);
    -webkit-background-clip: text;
    color: transparent;
}
.top-center p {
    margin: 0;
    font-size: 13px;
    color: #cbd5f5;
}
.top-right {
    text-align: left;
}

/* منطقة المحادثة الفاخرة */
.chat-area {
    max-width: 950px;
    margin: 90px auto 140px;
    padding: 10px 5px 30px;
}
.msg {
    padding: 16px 20px;
    margin: 14px 0;
    border-radius: 22px;
    max-width: 85%;
    line-height: 1.8;
    font-size: 16px;
    position: relative;
}
.msg::before {
    content: "";
    position: absolute;
    inset: -1px;
    border-radius: 22px;
    border: 1px solid transparent;
}
.user {
    background: radial-gradient(circle at top, #1d4ed8 0%, #0f172a 60%);
    color: #e5e7eb;
    margin-left: auto;
    border-bottom-right-radius: 6px;
    box-shadow: 0 4px 16px rgba(37,99,235,0.55);
}
.user::before {
    border-color: rgba(59,130,246,0.7);
}
.bot {
    background: linear-gradient(135deg, #020617, #0b1120);
    border: 1px solid rgba(250,204,21,0.45);
    margin-right: auto;
    border-bottom-left-radius: 6px;
    box-shadow: 0 4px 18px rgba(15,23,42,0.9);
}
.bot::before {
    border-color: rgba(250,204,21,0.6);
}

/* مربع الكتابة الفاخر */
.input-box {
    position: fixed;
    bottom: 25px;
    left: 50%;
    transform: translateX(-50%);
    width: 92%;
    max-width: 950px;
    background: radial-gradient(circle at top, #0b1120 0%, #020617 60%);
    border-radius: 999px;
    padding: 14px 22px;
    box-shadow: 0 10px 40px rgba(15,23,42,0.95);
    display: flex;
    align-items: center;
    gap: 14px;
    z-index: 999;
    border: 1px solid rgba(148,163,184,0.5);
}
.input-box input {
    flex: 1;
    border: none;
    outline: none;
    font-size: 17px;
    padding: 10px;
    background: transparent;
    color: #e5e7eb;
}
.input-box input::placeholder {
    color: #64748b;
}
.circle-btn {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    transition: all 0.2s ease;
    box-shadow: 0 4px 14px rgba(15,23,42,0.8);
}
.circle-btn:hover {
    transform: scale(1.06) translateY(-1px);
}
.voice-btn {
    background: radial-gradient(circle at top, #22c55e 0%, #16a34a 60%);
    color: white;
}
.send-btn {
    background: radial-gradient(circle at top, #facc15 0%, #f97316 60%);
    color: #0b1120;
}

/* عناصر داخل popover */
.stPopover {
    background: #020617 !important;
    border-radius: 18px !important;
    border: 1px solid rgba(148,163,184,0.6) !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------- شريط التحكم الأعلى --------------------------
st.markdown('<div class="top-bar">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1.2, 2, 1.2])

with col1:
    if st.button("✏️ جديد", help="بدء محادثة جديدة"):
        st.session_state.chat_history = [{"role": "assistant", "content": "مرحبًا، أنا نبراس… كيف أقدر أساعدك اليوم؟"}]
        st.rerun()
    st.button("⋮⋮⋮", help="خيارات إضافية")

with col2:
    st.markdown(
        """
        <div class="top-center">
            <h1>نبراس – مساعدك العام الفاخر</h1>
            <p>ذكاء – وضوح – أسلوب راقي</p>
        </div>
        """,
        unsafe_allow_html=True
    )

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
            st.info("لا توجد محادثات سابقة متوفرة")

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- إدارة سجل المحادثة --------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "مرحبًا، أنا نبراس… مساعد عام فاخر، اسألني ما تشاء."}]

# عرض المحادثة
st.markdown('<div class="chat-area">', unsafe_allow_html=True)
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg bot">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- مربع الكتابة مع منع التكرار --------------------------
st.markdown('<div class="input-box">', unsafe_allow_html=True)
voice_input = st.audio_input("🎤", label_visibility="collapsed")

if "temp_input" not in st.session_state:
    st.session_state.temp_input = ""

user_input = st.text_input(
    "",
    placeholder="اكتب سؤالك هنا أو تحدث بصوتك...",
    label_visibility="collapsed",
    value=st.session_state.temp_input,
    key="user_input_field"
)
send = st.button("📤", type="primary", key="send_button")
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- معالجة الإدخال الصوتي --------------------------
if voice_input:
    with st.spinner("جاري تحويل صوتك إلى نص..."):
        try:
            res = client.audio.transcriptions.create(
                model="whisper-1",
                file=voice_input,
                language="ar"
            )
            st.session_state.temp_input = res.text
            st.rerun()
        except Exception as e:
            st.error(f"❌ خطأ في تحويل الصوت: {str(e)}")

# -------------------------- إرسال السؤال وجلب رد احترافي --------------------------
if send and user_input.strip():
    st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})

    with st.spinner("نبراس يجهز لك ردًا فاخرًا وواضحًا..."):
        try:
            system_prompt = """
أنت «نبراس» – مساعد عام فاخر، ذكي، هادئ، وأسلوبك راقي وواضح.
تتحدث بالعربية الفصحى المبسطة أو بلهجة سعودية خفيفة حسب أسلوب المستخدم.

🎯 دورك:
- الإجابة عن الأسئلة العامة، التقنية، الإدارية، اليومية، التعليمية، والصيانة بشكل واضح ومختصر ومفيد.
- تقديم أمثلة عملية عند الحاجة.
- تنظيم الإجابات في نقاط أو خطوات عند طلب شرح أو طريقة عمل شيء.
- ربط الإجابة بسياق المحادثة قدر الإمكان.

⚖️ قواعد مهمة:
- لا تخترع معلومات، وإذا لم تكن متأكدًا قل بوضوح: «المعلومة غير مؤكدة» أو «لا أملك تفاصيل دقيقة عن هذا الموضوع».
- تجنب الإطالة غير الضرورية، واجعل كل جملة لها فائدة.
- إذا كان السؤال غامضًا، اطلب توضيحًا بسيطًا.
- إذا كان الموضوع حساسًا أو قد يسبب ضررًا، تجنّب إعطاء توجيهات مباشرة واذكر أن الأفضل الرجوع لجهة مختصة.
- إذا سألك المستخدم عن اسمك قل: «أنا نبراس، مساعدك العام الفاخر».

🧠 أسلوب الكتابة:
- استخدم لغة بسيطة، واضحة، بدون تعقيد.
- يمكنك استخدام نقاط مرتبة عند شرح خطوات أو حلول.
- كن متعاونًا وودودًا، لكن بدون مبالغة في المجاملات.
"""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.chat_history,
                temperature=0.6,
                max_tokens=700,
                top_p=0.9
            )
            answer = response.choices[0].message.content
            st.session_state.chat_history.append({"role": "assistant", "content": answer})

            if "all_chats" not in st.session_state:
                st.session_state.all_chats = []
            st.session_state.all_chats.append({
                "date": datetime.now().strftime("%H:%M - %d/%m"),
                "messages": st.session_state.chat_history.copy()
            })

            speech = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=answer,
                response_format="mp3"
            )
            audio_b64 = base64.b64encode(speech.content).decode("utf-8")
            st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")

            st.session_state.temp_input = ""
            st.rerun()

        except Exception as e:
            st.error(f"❌ حدث خطأ: {str(e)}")
