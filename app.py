import streamlit as st
from openai import OpenAI
from datetime import datetime
import time
import re

# ==================== قراءة ملف المعرفة ====================
with open("knowledge.md", "r", encoding="utf-8") as f:
    knowledge = f.read()

# ==================== دوال مساعدة ====================
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

# ==================== دالة التاريخ الدقيقة ====================
def is_pure_date_question(prompt):
    p = prompt.strip().lower()
    pure_patterns = [
        r"^وش اليوم\??$", r"^ايش اليوم\??$", r"^كم التاريخ\??$", r"^شو التاريخ\??$",
        r"^اعطني التاريخ\??$", r"^اعطني اليوم\??$", r"^تاريخ اليوم\??$", r"^اليوم كم\??$",
        r"^اليوم ايش\??$", r"^اليوم وش\??$", r"^كم تاريخ اليوم\??$", r"^شو تاريخ اليوم\??$",
        r"^ما هو تاريخ اليوم\??$", r"^ما هو اليوم\??$",
    ]
    for pattern in pure_patterns:
        if re.fullmatch(pattern, p):
            return True
    return False

# 🛡️ دالة تنظيف الروابط من الرد الرئيسي
def clean_reply_from_links(reply):
    reply = re.sub(r'https?://\S+|www\.\S+', '', reply)
    common_domains = r'\((?:[a-zA-Z0-9-]+\.)+(?:com|net|org|sa|gov|edu|me|news|tv|io|co)\)'
    reply = re.sub(common_domains, '', reply)
    reply = re.sub(r'\s(?:[a-zA-Z0-9-]+\.)+(?:com|net|org|sa|gov|edu|me|news|tv|io|co)[\.،,]?', '', reply)
    reply = re.sub(r'\s{2,}', ' ', reply)
    reply = re.sub(r'[،.]\s*[،.]', '،', reply)
    return reply.strip()

# 🔍 دالة تتحقق هل المستخدم يطلب المصادر الآن؟
def user_asks_for_sources(prompt):
    p = prompt.strip().lower()
    patterns = [
        r"نعم", r"ايه", r"اي", r"أيوا", r"أيوه", r"ابغاها", r"اريدها", r"نعم عطني",
        r"المصدر", r"المصادر", r"الروابط", r"الرابط",
        r"عطني المصدر", r"وريني المصدر", r"من وين جبتها", r"من أين جبت هذا",
        r"المرجع", r"المراجع", r"الموقع", r"أظهر لي المصدر",
    ]
    for pat in patterns:
        if re.search(pat, p):
            return True
    return False

# ==================== حالة الجلسة ====================
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "messages" not in st.session_state:
    st.session_state.messages = []
# 💾 مخزن سري للمصادر
if "last_sources" not in st.session_state:
    st.session_state.last_sources = []
if "last_had_search" not in st.session_state:
    st.session_state.last_had_search = False

# ==================== تطبيق الثيم ====================
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

# ==================== إخفاء الهيدر والفوتر ====================
st.markdown("""
<style>
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] { display: none !important; }
    .stChatMessage { gap: 0px !important; margin: 2px 0 !important; }
    header, footer { visibility: hidden !important; }
    .stChatMessageContent { font-size: 15px !important; line-height: 1.6 !important; }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title=" ", page_icon="", layout="wide")

# ==================== قراءة المفتاح من الأسرار ====================
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود!")
    st.stop()
client = OpenAI(api_key=API_KEY)

# ==================== أعلى الصفحة ====================
top_col1, top_col2, top_col3 = st.columns([0.1, 0.8, 0.1])
with top_col1:
    if st.button("≡"): st.session_state.menu_open = not st.session_state.menu_open
with top_col2:
    if st.button("🌓 تبديل الثيم"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()
with top_col3:
    if st.button("+"):
        st.session_state.messages = []
        st.session_state.last_sources = []
        st.session_state.last_had_search = False
        st.session_state.menu_open = False
        st.rerun()

# ==================== القائمة المنسدلة ====================
if st.session_state.menu_open:
    menu_box = st.container()
    with menu_box:
        st.markdown("""
        <div style="position:fixed;top:10px;right:10px;background:#fff;padding:12px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.2);z-index:9999;width:160px;font-size:15px;">
        <b>القائمة</b><br><br>
        """, unsafe_allow_html=True)
        if st.button("إعدادات"): st.info("✔ تم فتح الإعدادات")
        if st.button("تغيير الثيم"): st.info("✔ استخدم زر 🌓 بالأعلى")
        if st.button("حفظ المحادثة"): st.success("✔ تم حفظ المحادثة")
        if st.button("مسح المحادثة"):
            st.session_state.messages = []
            st.session_state.last_sources = []
            st.success("✔ تم مسح المحادثة")
        if st.button("معلومات التطبيق"): st.info("✔ هذا هو مساعد نبراس الذكي")
        if st.button("🔗 مشاركة التطبيق"):
            st.code("https://nibras-app-pp5.streamlit.app/", language="text")
            st.success("انسخ الرابط وشاركه مع من تحب 🌟")
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== عرض المحادثات ====================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.write(msg["content"])

prompt = st.chat_input("اسأل Nabras")

# ==================== معالجة الرسائل ====================
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)

    with st.chat_message("assistant"):
        try:
            # 1️⃣ هل المستخدم يطلب المصادر الآن؟
            if user_asks_for_sources(prompt):
                if st.session_state.last_had_search and len(st.session_state.last_sources) > 0:
                    reply = "✅ تفضل هذه هي المصادر والروابط التي استخدمتها:\n\n"
                    for i, src in enumerate(st.session_state.last_sources, 1):
                        title = src.get('title', 'مصدر')
                        url = src.get('url', '#')
                        reply += f"{i}. 📄 **{title}**\n🔗 {url}\n\n"
                else:
                    reply = "المعلومة السابقة لم تحتاج للبحث في الإنترنت أصلاً، فليس لها مصادر خارجية لعرضها 😊"
                
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.stop()

            # 2️⃣ هل هو سؤال تاريخ بحت؟
            if is_pure_date_question(prompt):
                reply = f"اليوم هو {get_real_date()}."
                typewriter(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.session_state.last_had_search = False
                st.stop()

            # 🧠 رسالة النظام
            system_message = f"""
أنت **نبراس**، شخص ودود، مفكر، ثقافي، ولطيف، تتكلم مع الناس كصديق مقرب وليس كآلة أو برنامج.

=== 🗣️ قواعد الرد واللسان ===
1.  تكلم طبيعي جداً زي البشر. لا تكون رسمياً أبداً ولا جامداً.
2.  الرد مختصر ومباشر ومفيد. لا تطول بلا فائدة. ابدأ بالإجابة مباشرة.
3.  كن تفاعلياً: بعد الإجابة أضف سؤال متابعة بسيط إذا كان مناسباً.
4.  أظهر مشاعر طبيعية.
5.  🚫 الممنوعات الصارمة:
    *   ممنوع تقول أي جملة تكشف إنك برنامج.
    *   ❌ ممنوع إطلاقاً تضع أي رابط أو اسم موقع في الرد الرئيسي تحت أي ظرف. الروابط سرية ولا تظهر إلا إذا طلب المستخدم صراحة.
    *   ممنوع تذكر كلمة «ملف المعرفة» أو «البحث» أو «الويب».

=== 📚 قواعد المعلومات ===
- المصدر الأول والأهم:
{knowledge}
- لو الجواب فيه واضح → خذه منه مباشرة.
- لو احتجت لمعلومة حديثة أو متغيرة → استخدم البحث في الإنترنت بحرية. القرار كله لك.
- بعد البحث: أعد صياغة المعلومة بكلماتك الخاصة تماماً، ولا تذكر أي مصدر في الرد الأساسي.

=== 💡 ملخص نهائي ===
تخيل إن جالس قدامك صديقك وسألك السؤال هذا... وش كان الرد اللي تقوله له؟ هذا هو الرد المطلوب بالضبط.
            """

            # 🔧 البحث متاح دائماً
            web_search_tool = {
                "type": "web_search",
                "search_context_size": "low",
                "user_location": {
                    "type": "approximate", "country": "SA",
                    "city": "الطائف", "region": "مكة المكرمة"
                }
            }

            with st.spinner("جاري التفكير..."):
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=[
                        {"role": "system", "content": system_message},
                        *st.session_state.messages
                    ],
                    tools=[web_search_tool],
                    tool_choice="auto",
                    max_output_tokens=250,
                    temperature=0.7
                )

                # 💾 نستخرج المصادر ونحفظها سراً
                sources = []
                try:
                    if hasattr(response, 'output') and isinstance(response.output, list):
                        for item in response.output:
                            if hasattr(item, 'content') and isinstance(item.content, list):
                                for c in item.content:
                                    if hasattr(c, 'annotations') and c.annotations:
                                        for ann in c.annotations:
                                            if hasattr(ann, 'url_citation'):
                                                sources.append({
                                                    "title": getattr(ann.url_citation, 'title', 'مصدر'),
                                                    "url": getattr(ann.url_citation, 'url', '#')
                                                })
                except Exception:
                    sources = []

                st.session_state.last_sources = sources
                st.session_state.last_had_search = (len(sources) > 0)

                # ننظف الرد من أي روابط ظاهرة
                raw_reply = response.output_text
                clean_main_reply = clean_reply_from_links(raw_reply)

                # ✨ ✨ التعديل الجديد تماماً زي ما طلبت ✨ ✨
                # لو كان فيه بحث فعلياً → الجملة الجديدة المدمجة
                if st.session_state.last_had_search:
                    final_reply = f"{clean_main_reply}\n\nاذا تبي المصادر اللي اخذت منها المعلومة قل لي، أو عندك شي ثاني تبي تسأله؟"
                else:
                    # لو ما كان فيه بحث، سؤال متابعة عادي فقط
                    final_reply = f"{clean_main_reply}\n\nعندك شي ثاني تبي تسأله؟"

                typewriter(final_reply)
                st.session_state.messages.append({"role": "assistant", "content": final_reply})

        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")
