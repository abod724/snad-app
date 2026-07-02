import streamlit as st
from openai import OpenAI
import base64

# ---------------- إعداد الصفحة ----------------
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- قراءة المفتاح ----------------
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("⚠️ المفتاح غير مضاف في إعدادات Streamlit")
    st.stop()

client = OpenAI(api_key=API_KEY)
# ---------------- تصميم الواجهة ----------------
st.markdown("""
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.stApp{
    background:#ffffff;
}

.title{
    text-align:center;
    font-size:38px;
    font-weight:bold;
    margin-top:15px;
    color:#111827;
}

.sub{
    text-align:center;
    color:#6b7280;
    margin-bottom:25px;
}

.msg{
    background:#f8fafc;
    border:1px solid #e5e7eb;
    border-radius:18px;
    padding:15px;
    margin-bottom:12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">نبراس</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">تحدث مع نبراس</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("☰ نبراس")
    if st.button("✏️ محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

audio = st.audio_input("🎤")

voice_text = ""
if audio:
    try:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio,
            language="ar"
        )
        voice_text = result.text
    except:
        st.error("تعذر تحويل الصوت.")

prompt = st.chat_input("تحدث مع نبراس")

if voice_text:
    prompt = voice_text

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    messages = [
        {
            "role": "system",
            "content": """
أنت مساعد ذكي اسمك نبراس.

تساعد المستخدمين في:
- البر والكشتات.
- الحلال والمواشي.
- الصيد والطيور المهاجرة.
- الأسئلة العامة.

أجب باختصار.
لا تكتب ردوداً طويلة إلا إذا طلب المستخدم التفصيل.
كن مؤدباً دائماً.
إذا سئلت عن اسمك فقل: اسمي نبراس.
"""
        }
    ]

    messages.extend(st.session_state.messages)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        max_completion_tokens=180
    )

    answer = response.choices[0].message.content

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

    st.rerun()

if st.session_state.messages:
    last = st.session_state.messages[-1]

    if last["role"] == "assistant":
        try:
            speech = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=last["content"],
                response_format="mp3"
            )

            audio_b64 = base64.b64encode(
                speech.content
            ).decode()

            st.audio(
                f"data:audio/mp3;base64,{audio_b64}"
            )
        except:
            pass
