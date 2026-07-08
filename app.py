import streamlit as st
from openai import OpenAI
import base64
from datetime import datetime
from serpapi import GoogleSearch

# -------------------------- إعدادات الصفحة --------------------------
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------- المفاتيح --------------------------
from openai import OpenAl
API_KEY = st.secrets.get("OPENAI_API_KEY")
response = client.responses.create)
 model="gpt-4o-mini"
 input="ابحث في الويب عن اخر التحديثات"
 tools[{"type":"web_search"}]

print(response.output_text)
if not API_KEY:
    st.error("⚠️ المفتاح غير مضاف في إعدادات Streamlit")
    st.stop()

if not SERPAPI_API_KEY:
    st.error("⚠️ مفتاح SerpAPI غير مضاف في إعدادات Streamlit")
    st.stop()

client = OpenAI(api_key=API_KEY)

# -------------------------- دالة البحث --------------------------
def search_google(query):
    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "num": 5
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        
        snippets = []
        if "organic_results" in results:
            for result in results["organic_results"][:5]:
                snippet = result.get("snippet", "")
                if snippet:
                    snippets.append(snippet)
        
        if snippets:
            return "\n".join(snippets)
        return "لم أجد نتائج بحث محددة."
    except Exception as e:
        return f"حدث خطأ في البحث: {str(e)}"

# -------------------------- واجهة بيضاء وسوداء (أنيقة) --------------------------
st.markdown("""
<style>
/* تنسيق عام */
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

/* ===== الشريط العلوي ===== */
.top-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: #ffffff;
    padding: 10px 20px;  /* تقليل المسافة */
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* القلم في اليسار مع العنوان */
.top-left {
    display: flex;
    align-items: center;
    gap: 8px; /* مسافة صغيرة بين القلم والعنوان */
}
.top-left .pen-icon {
    font-size: 22px;
    background: #f0f4ff;
    padding: 6px;
    border-radius: 10px;
    color: #1a1a1a;
}
.top-left .app-title {
    font-size: 22px;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0;
}

.top-center p {
    margin: 0;
    font-size: 13px;
    color: #6b7280;
}

/* ===== منطقة المحادثة ===== */
.chat-area {
    max-width: 850px;
    margin: 70px auto 100px;  /* تقليل المسافات */
    padding: 8px 5px 20px;   /* تقليل المسافات */
}

/* ===== تنسيق الرسائل ===== */
.msg {
    padding: 12px 16px;      /* تقليل المسافات */
    margin: 6px 0;           /* تقليل المسافات */
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

/* ===== مربع الكتابة (مختصر وأنيق) ===== */
div[data-testid="stChatInput"] {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    padding: 2px 12px !important;  /* تقليل المسافات */
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    margin-bottom: 10px !important;
}

div[data-testid="stChatInput"] input {
    color: #1a1a1a !important;
    font-weight: 500 !important;
    background: #ffffff !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;  /* تقليل المسافات */
    font-size: 15px !important;
}

div[data-testid="stChatInput"] input::placeholder {
    color: #9ca3af !important;
}

div[data-testid="stChatInput"] button {
    background: #1a1a1a !important;
    color: #ffffff !important;
    border-radius: 50% !important;
    padding: 6px !important;  /* تقليل المسافات */
}

/* ===== القائمة المنسدلة (بدون شرطتين) ===== */
div[data-testid="stPopover"] {
    border-radius: 12px !important;
    border: 1px solid #e5e7eb !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
    padding: 8px !important;
}

div[data-testid="stPopover"] button {
    border-bottom: none !important;  /* إزالة الشرطتين */
    padding: 8px 12px !important;
    border-radius: 8px !important;
    margin: 2px 0 !important;
    font-size: 14px !important;
}

div[data-testid="stPopover"] button:hover {
    background: #f3f4f6 !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------- الشريط العلوي --------------------------
st.markdown('<div class="top-bar">', unsafe_allow_html=True)

# العمود الأيسر: القلم + العنوان
col_left, col_center, col_right = st.columns([1.2, 2, 1.2])

with col_left:
    # القلم في اليسار مع العنوان
    st.markdown("""
    <div class="top-left">
        <span class="pen-icon">✏️</span>
        <span class="app-title">جديد نبراس</span>
    </div>
    """, unsafe_allow_html=True)

with col_center:
    st.markdown(
        """
        <div class="top-center">
            <p>مساعدك الذكي – بسيط، سريع، واضح</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_right:
    with st.popover("📋 المحادثات السابقة"):
        if "all_chats" not in st.session_state:
            st.session_state.all_chats = []
        if st.session_state.all_chats:
            for i, c in enumerate(st.session_state.all_chats):
                # إزالة الشرطتين من الأزرار (تمت عبر CSS)
                if st.button(f"محادثة {i+1} - {c['date']}", use_container_width=True):
                    st.session_state.chat_history = c["messages"]
                    st.rerun()
        else:
            st.info("لا توجد محادثات سابقة")

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- سجل المحادثة --------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "مرحبًا، أنا نبراس… كيف أقدر أساعدك اليوم؟"}]

# عرض المحادثة
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

        with st.spinner("نبراس يبحث..."):
            try:
                search_results = search_google(query)

                system_prompt = f"""
أنت «نبراس» – مساعد ذكي، أسلوبك بسيط وواضح.
تتحدث بالعربية الفصحى أو بلهجة سعودية خفيفة.

🎯 دورك:
- الإجابة عن الأسئلة العامة، التقنية، اليومية، التعليمية.
- قدّم أمثلة عملية عند الحاجة.
- نظّم الإجابات في نقاط إذا كان السؤال يتطلب شرحاً.

⚖️ قواعد:
- لا تخترع معلومات، وإذا لم تكن متأكداً قل: «المعلومة غير مؤكدة».
- تجنب الإطالة غير الضرورية.
- إذا كان السؤال غامضاً، اطلب توضيحاً.
- إذا سألك عن اسمك: «أنا نبراس، مساعدك الذكي».

📌 معلومات محدثة من البحث:
{search_results}
"""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *st.session_state.chat_history
                    ]
                )

                answer = response.choices[0].message.content

                st.session_state.chat_history.append({"role": "assistant", "content": answer})

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
                except Exception as e:
                    st.warning(f"⚠️ خطأ في الصوت: {str(e)}")

                st.rerun()

            except Exception as e:
                st.error(f"❌ خطأ: {str(e)}")
