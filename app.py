import streamlit as st
import time

st.set_page_config(page_title="نبراس", page_icon="⚡", layout="wide")

st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #f5f7fa; }
.chat-container { max-width: 750px; margin: 80px auto 100px; padding: 0 20px; }
.msg-user { padding: 12px 18px; margin: 6px 0 6px auto; background: #e9ecef; border-radius: 20px 20px 4px 20px; max-width: 75%; width: fit-content; }
.msg-bot { padding: 12px 18px; margin: 6px auto 6px 0; background: #ffffff; border-radius: 20px 20px 20px 4px; max-width: 75%; width: fit-content; box-shadow: 0 2px 12px rgba(0,0,0,0.04); }
.time-badge { font-size: 10px; color: #aaa; margin-top: 4px; display: block; }
.top-bar {
    position: fixed; top: 0; left: 0; right: 0;
    background: rgba(255,255,255,0.92); backdrop-filter: blur(12px);
    padding: 12px 24px; border-bottom: 1px solid rgba(0,0,0,0.04);
    display: flex; justify-content: space-between; align-items: center;
    z-index: 1000; height: 64px;
}
.top-bar .brand { font-size: 18px; font-weight: 600; color: #1a1a1a; }
.top-bar .brand span { background: #1a1a1a; color: white; border-radius: 50%; padding: 4px 10px; margin-left: 8px; font-size: 14px; }
.stChatInput {
    border-radius: 40px !important; border: 1px solid rgba(0,0,0,0.04) !important;
    background: rgba(255,255,255,0.9) !important; backdrop-filter: blur(10px) !important;
    padding: 4px 16px !important;
    position: fixed !important; bottom: 20px !important; left: 50% !important;
    transform: translateX(-50%) !important;
    width: 750px !important; max-width: 94% !important; z-index: 999 !important;
}
.stChatInput input { border-radius: 40px !important; padding: 12px 16px !important; font-size: 15px !important; }
.stChatInput button { background: #1a1a1a !important; border-radius: 50% !important; padding: 6px 14px !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ===== الشريط العلوي =====
st.markdown("""
<div class="top-bar">
    <div class="brand"><span>⚡</span> نبراس</div>
    <button onclick="location.reload()" style="background:#1a1a1a;color:white;border:none;padding:8px 20px;border-radius:30px;font-size:14px;cursor:pointer;">➕ دردشة جديدة</button>
</div>
""", unsafe_allow_html=True)

# ===== عرض المحادثة =====
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">{msg["content"]}<span class="time-badge">{time.strftime("%I:%M %p")}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-bot">{msg["content"]}<span class="time-badge">{time.strftime("%I:%M %p")}</span></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ===== القائمة المنسدلة (مثل ChatGPT) =====
options = [
    "📝 تلخيص نص", "💡 فكرة مشروع", "📚 شرح درس", "🧠 حل مسألة رياضية",
    "✍️ كتابة مقال", "🌍 ترجمة نص", "🔍 بحث عن موضوع", "📊 تحليل بيانات",
    "🎨 تصميم فكرة", "📖 تعريف مصطلح", "🗺️ خطة دراسة", "💼 سيرة ذاتية",
    "📧 كتابة بريد", "🎤 خطاب", "📝 مراجعة نص", "🧩 لغز أو سؤال",
    "📈 توقع مستقبلي", "🛠️ حل مشكلة تقنية", "🎯 نصائح يومية", "📋 قائمة مهام"
]

selected = st.selectbox(
    "اختر خدمة سريعة:",
    options,
    index=None,
    placeholder="📌 اختر من القائمة...",
    key="quick_action"
)

if selected:
    # ردود فورية (بدون انتظار)
    quick_responses = {
        "📝 تلخيص نص": "أرسل النص الذي تريد تلخيصه وسأقوم بتلخيصه فوراً.",
        "💡 فكرة مشروع": "فكرة مشروع: تطبيق لإدارة الوقت باستخدام الذكاء الاصطناعي.",
        "📚 شرح درس": "أخبرني بالدرس الذي تريد شرحه وسأشرحه لك بأسلوب مبسط.",
        "🧠 حل مسألة رياضية": "اكتب المسألة الرياضية وسأحلها لك خطوة بخطوة.",
        "✍️ كتابة مقال": "أخبرني عن موضوع المقال وسأكتبه لك.",
        "🌍 ترجمة نص": "أرسل النص وسأترجمه لأي لغة تريد.",
        "🔍 بحث عن موضوع": "اكتب الموضوع وسأقدم لك ملخصاً عنه.",
        "📊 تحليل بيانات": "أرفق البيانات وسأقوم بتحليلها.",
        "🎨 تصميم فكرة": "أخبرني عن فكرتك وسأطورها.",
        "📖 تعريف مصطلح": "اكتب المصطلح وسأعرفه لك.",
        "🗺️ خطة دراسة": "أخبرني عن المادة وسأضع لك خطة دراسة.",
        "💼 سيرة ذاتية": "أرسل معلوماتك وسأكتب سيرتك الذاتية.",
        "📧 كتابة بريد": "أخبرني بمحتوى البريد وسأكتبه لك.",
        "🎤 خطاب": "أخبرني عن المناسبة وسأكتب لك خطاباً.",
        "📝 مراجعة نص": "أرسل النص وسأقوم بمراجعته.",
        "🧩 لغز أو سؤال": "إليك لغز: ما هو الشيء الذي يكتب ولا يقرأ؟ الجواب: القلم.",
        "📈 توقع مستقبلي": "التوقعات تشير إلى ازدياد استخدام الذكاء الاصطناعي في التعليم.",
        "🛠️ حل مشكلة تقنية": "أخبرني عن المشكلة وسأقدم لك الحل.",
        "🎯 نصائح يومية": "نصيحة اليوم: خصص 10 دقائق للقراءة يومياً.",
        "📋 قائمة مهام": "إليك قائمة مهام يومية: 1) قراءة، 2) تمرين، 3) عمل."
    }

    reply = quick_responses.get(selected, "شكراً لاختيارك! كيف يمكنني مساعدتك أكثر؟")
    st.session_state.messages.append({"role": "user", "content": selected})
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# ===== مربع الكتابة الرئيسي =====
prompt = st.chat_input("اكتب سؤالك هنا...", key="main_chat")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    # رد وهمي سريع (لأننا لا نريد انتظار GPT في الوقت الحالي)
    st.session_state.messages.append({"role": "assistant", "content": f"شكراً لسؤالك: '{prompt}'. سأقوم بالرد عليك قريباً."})
    st.rerun()
