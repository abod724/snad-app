import streamlit as st
from openai import OpenAI
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
# إعدادات ثابتة
st.set_page_config(page_title="نبراس", page_icon="💬", layout="centered", initial_sidebar_state="collapsed")

# واجهة ثابتة ومريحة
st.markdown("""
<style>
* {direction: rtl; text-align: right; font-family: 'Cairo', sans-serif;}
#MainMenu, footer, header {display: none !important;}
.stApp {background: #f7f9fc; max-width: 850px; margin: 0 auto; padding: 20px;}
h1 {color: #2563eb; text-align: center;}
.msg {padding: 14px 18px; margin: 10px 0; border-radius: 16px; line-height: 1.6;}
.user {background: #2563eb; color: white; margin-left: auto; max-width: 80%;}
.bot {background: white; border: 1px solid #e2e8f0; margin-right: auto; max-width: 80%;}
</style>
""", unsafe_allow_html=True)

# ✅ الكود يجلب المفتاح تلقائياً من المكان الآمن
API_KEY = st.secrets.get("OPENAI_API_KEY")

if not API_KEY:
    st.error("⚠️ المفتاح غير مضاف بعد! اذهب للإعدادات ← المفاتيح السرية وأضف: OPENAI_API_KEY")
    st.stop()

client = OpenAI(api_key=API_KEY)

# المحتوى
st.title("💬 نبراس — مساعدك الذكي")

if "chat" not in st.session_state:
    st.session_state.chat = [{"role":"assistant", "content":"أهلاً وسهلاً! أنا نبراس، اسألني أي شيء وسأجيبك دائماً."}]

for msg in st.session_state.chat:
    st.markdown(f'<div class="msg {msg["role"]}">{msg["content"]}</div>', unsafe_allow_html=True)

سؤال = st.text_input("", placeholder="اكتب سؤالك هنا...", label_visibility="collapsed")
if st.button("إرسال") and سؤال.strip():
    st.session_state.chat.append({"role":"user", "content":سؤال.strip()})
    with st.spinner("أجيبك..."):
        رد = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"system","content":"أنت نبراس، أجب بالعربية بوضوح، لا تقل لا أعرف، تغطي كل المجالات."}, *st.session_state.chat],
            temperature=0.7,
            max_tokens=400
        )
        st.session_state.chat.append({"role":"assistant", "content":رد.choices[0].message.content})
    st.rerun()
