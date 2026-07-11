import streamlit as st
from openai import OpenAI
import os

# ============================================================
# إعدادات الصفحة
# ============================================================
st.set_page_config(
    page_title="نبراس",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# المفتاح والعميل
# ============================================================
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير مضاف")
    st.stop()
client = OpenAI(api_key=API_KEY)

# ============================================================
# ذاكرة المحادثة
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "أنت نبراس، صديق ذكي ودود، تجيب بأسلوب بسيط وواضح."},
        {"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}
    ]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ============================================================
# مترجم لغة عين (أداة جانبية)
# ============================================================
def عين_مترجم():
    st.subheader("🧠 مترجم لغة عين")
    st.caption("اكتب كوداً بلغة عربية (عين) وسيترجم إلى بايثون وينفذ.")

    html_code = """
    <html>
    <head>
      <script src="https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js"></script>
      <style>
        body { font-family: sans-serif; direction: rtl; background: transparent; padding: 10px; }
        textarea { width: 100%; height: 120px; font-family: monospace; }
        #الناتج { background: #fff; padding: 10px; margin-top: 10px; border: 1px solid #ccc; white-space: pre; }
        button { padding: 8px 16px; margin-top: 8px; margin-left: 5px; }
      </style>
    </head>
    <body>
    <textarea id="كود_عين">متغير العدد = 5
إذا (العدد > 3) {
  اطبع "العدد أكبر من 3"
} آخر {
  اطبع "العدد صغير"
}</textarea><br>
    <button onclick="شغل()">▶️ ترجمة وتشغيل</button>
    <button onclick="احفظ()">💾 حفظ الكود</button>
    <button onclick="انسخ()">📋 نسخ الناتج</button>
    <div id="الناتج"></div>
    <script>
    let جاهز = loadPyodide();

    async function شغل() {
      const كود = document.getElementById("كود_عين").value;
      const بايثون = ترجم(كود);
      const بايثون_جاهز = await جاهز;
      try {
        await بايثون_جاهز.runPythonAsync(`\n${بايثون}`);
        document.getElementById("الناتج").innerText = "✅ تم التنفيذ بنجاح";
      } catch (خطأ) {
        document.getElementById("الناتج").innerText = "❌ خطأ: " + خطأ;
      }
    }

    function ترجم(كود) {
      كود = كود.replace(/متغير\s+(\w+)\s*=\s*(.+)/g, "$1 = $2");
      كود = كود.replace(/اطبع\s+\"(.+?)\"/g, 'print("$1")');
      كود = كود.replace(/إذا\s*\((.+?)\)\s*\{/g, "if ($1):");
      كود = كود.replace(/\}\s*آخر\s*\{/g, "else:");
      كود = كود.replace(/\u0643\u0631\u0631 من (\d+) إلى (\d+)\s*\{/g, "for i in range($1, $2+1):");
      كود = كود.replace(/\}/g, "");

      let أسطر = كود.split("\n");
      let مسافة = "";
      let نتيجة = "";
      for (let سطر of أسطر) {
        سطر = سطر.trim();
        if (سطر.endsWith(":")) {
          نتيجة += مسافة + سطر + "\n";
          مسافة += "    ";
        } else {
          نتيجة += مسافة + سطر + "\n";
        }
      }
      return نتيجة;
    }

    function احفظ() {
      const كود = document.getElementById("كود_عين").value;
      const ملف = new Blob([كود], { type: "text/plain" });
      const رابط = document.createElement("a");
      رابط.href = URL.createObjectURL(ملف);
      رابط.download = "الكود.ain";
      رابط.click();
    }

    function انسخ() {
      const نص = document.getElementById("الناتج").innerText;
      navigator.clipboard.writeText(نص).then(() => {
        alert("تم نسخ الناتج!");
      });
    }
    </script>
    </body>
    </html>
    """
    st.components.v1.html(html_code, height=450, scrolling=True)

# ============================================================
# الشريط الجانبي (الأزرار والمترجم)
# ============================================================
with st.sidebar:
    st.markdown("### 💬 نبراس")
    st.markdown("---")
    
    if st.button("➕ محادثة جديدة", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": "أنت نبراس، صديق ذكي ودود، تجيب بأسلوب بسيط وواضح."},
            {"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}
        ]
        st.rerun()
    
    st.markdown("### 📋 المحادثات السابقة")
    if st.session_state.chat_history:
        for i, chat in enumerate(st.session_state.chat_history[::-1]):
            if st.button(f"💬 محادثة {i+1}", key=f"side_{i}", use_container_width=True):
                st.session_state.messages = chat
                st.rerun()
    else:
        st.info("لا توجد محادثات سابقة")
    
    st.markdown("---")
    with st.expander("🧠 مترجم لغة عين", expanded=False):
        عين_مترجم()

# ============================================================
# CSS لتثبيت الشريط العلوي
# ============================================================
st.markdown("""
<style>
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background: #f7f7f8; }

    .top-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: #ffffff;
        padding: 6px 20px;
        border-bottom: 1px solid #e5e5e5;
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 1000;
        height: 48px;
    }

    .chat-container {
        max-width: 750px;
        margin: 70px auto 80px;
        padding: 0 20px;
    }

    .msg-user {
        padding: 10px 16px;
        margin: 4px 0 8px auto;
        background: #e9ecef;
        border-radius: 18px;
        border-bottom-right-radius: 4px;
        max-width: 80%;
        width: fit-content;
        color: #1a1a1a;
        font-size: 15px;
        line-height: 1.6;
        clear: both;
    }
    .msg-bot {
        padding: 10px 16px;
        margin: 4px auto 8px 0;
        background: #ffffff;
        border-radius: 18px;
        border-bottom-left-radius: 4px;
        max-width: 80%;
        width: fit-content;
        color: #1a1a1a;
        font-size: 15px;
        line-height: 1.6;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        clear: both;
    }

    .stChatInput {
        border-radius: 30px !important;
        border: 1px solid #e5e5e5 !important;
        background: #ffffff !important;
        padding: 2px 12px !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.02) !important;
        position: fixed !important;
        bottom: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 750px !important;
        max-width: 92% !important;
        z-index: 999 !important;
    }
    .stChatInput input {
        border-radius: 30px !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
        background: transparent !important;
    }
    .stChatInput button {
        background: #1a1a1a !important;
        border-radius: 50% !important;
        padding: 4px 12px !important;
        color: white !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# الشريط العلوي (أزرار)
# ============================================================
st.markdown("""
<div class="top-bar">
    <span>💬</span>
    <div></div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 6, 1])

with col1:
    if st.button("⊕", key="new_chat", help="محادثة جديدة"):
        st.session_state.messages = [
            {"role": "system", "content": "أنت نبراس، صديق ذكي ودود، تجيب بأسلوب بسيط وواضح."},
            {"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}
        ]
        st.rerun()

with col3:
    with st.popover("☰"):
        st.markdown("### 📋 المحادثات السابقة")
        if st.button("➕ محادثة جديدة", use_container_width=True):
            st.session_state.messages = [
                {"role": "system", "content": "أنت نبراس، صديق ذكي ودود، تجيب بأسلوب بسيط وواضح."},
                {"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}
            ]
            st.rerun()
        st.markdown("---")
        if st.session_state.chat_history:
            for i, chat in enumerate(st.session_state.chat_history[::-1]):
                if st.button(f"💬 محادثة {i+1}", key=f"pop_{i}", use_container_width=True):
                    st.session_state.messages = chat
                    st.rerun()
        else:
            st.info("لا توجد محادثات سابقة")

# ============================================================
# عرض المحادثة
# ============================================================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f'<div class="msg-bot">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 🟢 أيقونة "ولد" فوق مربع الكتابة
# ============================================================
st.markdown("""
<div style="
    max-width: 750px;
    margin: 0 auto 5px;
    padding: 0 20px;
    text-align: center;
    position: relative;
    z-index: 999;
">
    <span style="
        font-size: 32px;
        background: #ffffff;
        padding: 6px 18px;
        border-radius: 50px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        border: 1px solid #e5e5e5;
        display: inline-block;
    ">👦</span>
</div>
""", unsafe_allow_html=True)

# ============================================================
# مربع الإدخال
# ============================================================
prompt = st.chat_input("اكتب سؤالك هنا...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("نبراس يبحث ويفكر..."):
            try:
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=st.session_state.messages,
                    tools=[{"type": "web_search"}],
                    max_output_tokens=500
                )
                reply = response.output_text
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.session_state.chat_history.append(st.session_state.messages.copy())
            except Exception as e:
                st.error(f"⚠️ خطأ: {str(e)}")
