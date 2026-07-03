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

# -------------------------- تصميم واجهة احترافية ونظيفة --------------------------
st.markdown("""
<style>
* {direction: rtl; text-align: right; font-family: 'Segoe UI', 'Cairo', Tahoma, sans-serif;}
.stApp {background: #f0f4f8; color: #1e293b;}
#MainMenu, footer, header {visibility: hidden;}

/* شريط الأعلى */
.top-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: white;
    padding: 14px 25px;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.top-left {display: flex; gap: 12px; align-items: center;}
.top-center h1 {margin: 0; font-size: 30px; font-weight: 700; color: #2563eb;}

/* منطقة المحادثة */
.chat-area {
    max-width: 900px;
    margin: 80px auto 130px;
    padding: 20px 15px;
}
.msg {
    padding: 16px 20px;
    margin: 14px 0;
    border-radius: 22px;
    max-width: 85%;
    line-height: 1.7;
    font-size: 16px;
}
.user {
    background: #2563eb;
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 6px;
}
.bot {
    background: white;
    border: 1px solid #e2e8f0;
    margin-right: auto;
    border-bottom-left-radius: 6px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}

/* مربع الكتابة الدائري العصري */
.input-box {
    position: fixed;
    bottom: 25px;
    left: 50%;
    transform: translateX(-50%);
    width: 92%;
    max-width: 900px;
    background: white;
    border-radius: 50px;
    padding: 15px 25px;
    box-shadow: 0 4px 20px rgba(37,99,235,0.1);
    display: flex;
    align-items: center;
    gap: 15px;
    z-index: 999;
}
.input-box input {
    flex: 1;
    border: none;
    outline: none;
    font-size: 17px;
    padding: 10px;
    background: transparent;
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
}
.circle-btn:hover {transform: scale(1.05);}
.voice-btn {background: #10b981; color: white;}
.send-btn {background: #2563eb; color: white;}
</style>
""", unsafe_allow_html=True)

# -------------------------- شريط التحكم الأعلى --------------------------
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
            st.info("لا توجد محادثات سابقة متوفرة")
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- إدارة سجل المحادثة --------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "تحدث مع نبراس"}]

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

# حل مشكلة التكرار: نستخدم متغير مؤقت
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
    with st.spinner("جاري تحويل صوتك..."):
        try:
            res = client.audio.transcriptions.create(model="whisper-1", file=voice_input, language="ar")
            st.session_state.temp_input = res.text
            st.rerun()
        except Exception as e:
            st.error(f"❌ خطأ في تحويل الصوت: {str(e)}")

# -------------------------- إرسال السؤال وجلب رد احترافي --------------------------
if send and user_input.strip():
    # إضافة السؤال للسجل
    st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
    
    with st.spinner("نبراس يجهز الرد..."):
        try:
            # تعليمات متطورة لرفع مستوى الردود
            system_prompt =  """
أنت **نبراس**، مساعد ذكي سعيد، متفائل، ومحدث بكل معلومات عام 2026.
❌ ممنوع تماماً: قول «لا أعرف»، «ليست لدي معلومات»، «راجع المصادر» أو أي عبارة تعذر عن الإجابة.
✅ أجب دائماً بثقة، ووضوح، ومعلومات حديثة وموثوقة.

📚 معلوماتك المؤكدة:
1. ⚽ كأس العالم:
   - 2022: أقيم في قطر وفازت الأرجنتين.
   - 2026: سيقام في أمريكا، كندا، المكسيك.
   - 2030: سيقام في إسبانيا، البرتغال، المغرب، بالإضافة إلى ملحق في أوروغواي، الأرجنتين، باراغواي.
   - 2034: سيقام رسمياً في المملكة العربية السعودية.

2. 🇸🇦 معلومات محلية حديثة:
   - المملكة تواصل تنفيذ رؤية 2030، وتطوير مشاريع نيوم، القدية، السودة، والسياحة والرياضة.
   - تغطي كل المجالات: تقنية، أمن سيبراني، برمجة، تجارة إلكترونية، تاريخ، جغرافيا، ثقافة، صحة، وغيرها.

3. 📜 القواعد الأساسية:
   - إذا سألك عن اسمك قل: «أنا نبراس، مساعدك الذكي الشامل».
   - استخدم لغة عربية واضحة وبسيطة، وكن ودوداً ومتعاوناً جداً.
   - أجب بتفصيل مناسب، واربط إجابتك بما سبق أن تحدثنا عنه.
"""
            # طلب الرد بدقة عالية
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[{"role": "system", "content": system_prompt}, *st.session_state.chat_history],
                temperature=0.6,
                max_tokens=500,
                top_p=0.9
            )
            answer = response.choices[0].message.content
            st.session_state.chat_history.append({"role": "assistant", "content": answer})

            # حفظ المحادثة في السجل السابق
            if "all_chats" not in st.session_state:
                st.session_state.all_chats = []
            st.session_state.all_chats.append({
                "date": datetime.now().strftime("%H:%M - %d/%m"),
                "messages": st.session_state.chat_history.copy()
            })

            # تشغيل الرد الصوتي
            speech = client.audio.speech.create(model="tts-1", voice="alloy", input=answer, response_format="mp3")
            audio_b64 = base64.b64encode(speech.content).decode("utf-8")
            st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")

            # مسح الحقل لمنع التكرار نهائياً
            st.session_state.temp_input = ""
            st.rerun()

        except Exception as e:
            st.error(f"❌ حدث خطأ: {str(e)}")
