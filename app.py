import streamlit as st
from openai import OpenAI
from datetime import datetime
import time
import re

# ==================== قراءة ملف المعرفة (كما هي بدون أي تغيير) ====================
with open("knowledge.md", "r", encoding="utf-8") as f:
    knowledge = f.read()

# ==================== دوال مساعدة (كما هي بدون أي تغيير) ====================
def typewriter(text):
    placeholder = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        placeholder.write(displayed)
        time.sleep(0.01)

def get_real_date():
    now = datetime.now()
    return now.strftime("%A، %d %B %Y")

# ==================== دالة تحديد الحاجة لبحث ويب (كما هي بدون أي تغيير) ====================
def needs_web_search(prompt):
    prompt_clean = prompt.strip().lower()
    
    # ❌ لا تحتاج بحث
    no_search_patterns = [
        r"^(سلام|مرحبا|هاي|هلا|أهلا)",
        r"كيف حالك|شلونك|شخبارك",
        r"من أنت|مين أنت|شنو اسمك",
        r"شكرا|مشكور|تسلم",
        r"مع السلامة|باي|وداعا",
        r"^(اكتب|صيغ|أعطني) (نص|رسالة|قصة|شعر|كلام)",
        r"اشرح لي|علمني|ما هو تعريف",
        r"حل مسألة|حل معادلة|احسب",
    ]
    for pattern in no_search_patterns:
        if re.search(pattern, prompt_clean):
            return False

    # ✅ تحتاج بحث ويب
    search_patterns = [
        r"اليوم|هذا الأسبوع|هذا الشهر|هذه السنة|الآن|حاليا|آخر|أحدث|جديد|مؤخرا",
        r"تاريخ اليوم|كم التاريخ|وش اليوم",
        r"عام 202[4-9]|عام 203",
        r"خبر|أخبار|ماذا حدث|حدث مؤخرا|حادث|كارثة|إطلاق|تصريح",
        r"سعر|سعر اليوم|كم يساوي|كم قيمة|سوق|أسهم|عملة|صرف|ذهب|نفط|بتكوين",
        r"طقس|حرارة|درجة الحرارة|مطر|رياح",
        r"مباراة|نتيجة|جدول|دوري|كأس|أبطال|المنتخب",
        r"فلم جديد|مسلسل جديد|موعد عرض|حلقة جديدة",
        r"إحصاء|نسبة|عدد السكان|معدل|تقرير رسمي|بيانات",
        r"موعد اختبار|موعد تسجيل|شروط القبول|تقديرات|نتائج الاختبارات",
        r"ابحث لي|ابحث في|تفقد لي|شوف لي|أريد معلومات عن|هل يوجد",
    ]
    
    for pattern in search_patterns:
        if re.search(pattern, prompt_clean):
            return True

    return False

# ==================== حالة الجلسة (كما هي بدون أي تغيير) ====================
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False

if "theme" not in st.session_state:
    st.session_state.theme = "light"

# ==================== تطبيق الثيم (كما هي بدون أي تغيير) ====================
if st.session_state.theme == "dark":
    st.markdown("""
    <style>
        .stApp { background-color: #1e1e1e !important; }
        .stChatMessageContent { color: white !important; }
        .stButton>button { background-color: #333 !important; color: white !important; }
        .stTextInput>div>div>input { background-color: #333 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp { background-color: white !important; }
        .stChatMessageContent { color: black !important; }
        .stButton>button { background-color: #f0f0f0 !important; color: black !important; }
        .stTextInput>div>div>input { background-color: white !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# ==================== إخفاء الهيدر والفوتر (كما هي بدون أي تغيير) ====================
st.markdown("""
<style>
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    .stChatMessage {
        gap: 0px !important;
        margin: 2px 0 !important;
    }
    header, footer {
        visibility: hidden !important;
    }
    .stChatMessageContent {
        font-size: 15px !important;
        line-height: 1.6 !important;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title=" ", page_icon="", layout="wide")

# ==================== قراءة المفتاح من صندوق الأسرار (كما هي بدون أي تغيير تماماً) ====================
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود!")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ==================== أعلى الصفحة (كما هي بدون أي تغيير) ====================
top_col1, top_col2, top_col3 = st.columns([0.1, 0.8, 0.1])

with top_col1:
    if st.button("≡"):
        st.session_state.menu_open = not st.session_state.menu_open

with top_col2:
    if st.button("🌓 تبديل الثيم"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()

with top_col3:
    if st.button("+"):
        st.session_state.messages = []
        st.session_state.menu_open = False
        st.rerun()

# ==================== القائمة المنسدلة (كما هي بدون أي تغيير) ====================
if st.session_state.menu_open:
    menu_box = st.container()
    with menu_box:
        st.markdown("""
        <div style="
            position: fixed;
            top: 10px;
            right: 10px;
            background: #ffffff;
            padding: 12px;
            border-radius: 8px;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.2);
            z-index: 9999;
            width: 160px;
            font-size: 15px;
        ">
        <b>القائمة</b><br><br>
        """, unsafe_allow_html=True)

        if st.button("إعدادات"):
            st.info("✔ تم فتح الإعدادات")

        if st.button("تغيير الثيم"):
            st.info("✔ استخدم زر 🌓 بالأعلى لتبديل الثيم")

        if st.button("حفظ المحادثة"):
            st.success("✔ تم حفظ المحادثة")

        if st.button("مسح المحادثة"):
            st.session_state.messages = []
            st.success("✔ تم مسح المحادثة")

        if st.button("معلومات التطبيق"):
            st.info("✔ هذا هو مساعد نبراس الذكي")

        if st.button("🔗 مشاركة التطبيق"):
            st.code("https://nibras-app-pp5.streamlit.app/", language="text")
            st.success("انسخ الرابط وشاركه مع من تحب 🌟")

        st.markdown("</div>", unsafe_allow_html=True)

# ==================== المحادثات (كما هي بدون أي تغيير) ====================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("اسأل Nabras")

# ==================== معالجة الرسائل مع إضافة اسم ملف المعرفة ====================
if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            # ⭐ نظام التاريخ (كما هو بدون أي تغيير)
            explicit_date = (
                "وش اليوم" in prompt or
                "كم التاريخ" in prompt or
                "اعطني التاريخ" in prompt or
                "اعطني اليوم" in prompt or
                "تاريخ اليوم" in prompt or
                "اليوم كم" in prompt
            )

            if explicit_date:
                reply = f"اليوم هو {get_real_date()}."
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.stop()

            # ✨ القرار الذكي للبحث (كما هو بدون أي تغيير)
            use_web = needs_web_search(prompt)

            # 🆕 هنا فقط تم إضافة اسم الملف بشكل صريح داخل رسالة النظام
            # كل باقي المعاملات كما هي بالضبط
            system_message = f"""
اسم ملف المعرفة الأساسي الذي تعتمد عليه بالكامل هو: knowledge.md
هذا الملف هو المرجع الأول والأعلى أولوية في كل الردود، قبل أي مصدر آخر.
إذا وجدت الإجابة في ملف knowledge.md فلا تستخدم أي مصدر آخر أبداً.
البحث في الويب يُستخدم فقط كمكمل إذا لم تجد المعلومة في الملف، أو إذا كانت المعلومة متغيرة وتحتاج لتحديث لحظي.

--- محتوى ملف المعرفة knowledge.md ---
{knowledge}
            """

            api_params = {
                "model": "gpt-4o-mini",
                "input": [
                    # ✅ تم استبدال knowledge المباشرة بـ system_message التي تحتوي على اسم الملف
                    {"role": "system", "content": system_message},
                    *st.session_state.messages
                ],
                "max_output_tokens": 200,
                "temperature": 0.3
            }

            # 🚀 إضافة أداة البحث عند الحاجة (كما هي بدون أي تغيير)
            if use_web:
                api_params["tools"] = [{
                    "type": "web_search",
                    "search_context_size": "low",
                    "user_location": {
                        "type": "approximate",
                        "country": "SA",
                    }
                }]
                spinner_text = "🔍 جاري البحث عن أحدث المعلومات..."
            else:
                spinner_text = "جاري التفكير..."

            # ⭐ استدعاء الـ API (كما هو بدون أي تغيير)
            with st.spinner(spinner_text):
                response = client.responses.create(**api_params)

                reply = response.output_text
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
