import streamlit as st
from openai import OpenAI
import os
import base64

st.set_page_config(page_title="نبراس", page_icon="💬", layout="wide", initial_sidebar_state="collapsed")

# ================================
# 1. المفتاح والعميل
# ================================
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير مضاف")
    st.stop()
client = OpenAI(api_key=API_KEY)

# ================================
# 2. الذاكرة
# ================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "أنت نبراس، صديق ذكي ودود، تجيب بأسلوب بسيط وواضح."},
        {"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}
    ]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ================================
# 3. مترجم لغة عين (أداة جانبية)
# ================================
def عين_مترجم():
    st.subheader("🧠 مترجم لغة عين")
    st.caption("اكتب كوداً بلغة عربية (عين) وسيترجم إلى بايثون وينفذ.")
    st.components.v1.html("""
    <html>
    <head>
      <script src="https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js"></script>
      <style>
        body { font-family: sans-serif; direction: rtl; background: transparent; padding: 10px; }
        textarea { width: 100%; height: 100px; font-family: monospace; }
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
    <div id="الناتج"></div>
    <script>
    let جاهز = loadPyodide();

    async function شغل() {
      const كود = document.getElementById("كود_عين").value;
      let بايثون = كود;
      بايثون = بايثون.replace(/متغير\s+(\w+)\s*=\s*(.+)/g, "$1 = $2");
      بايثون = بايثون.replace(/اطبع\s+\"(.+?)\"/g, 'print("$1")');
      بايثون = بايثون.replace(/إذا\s*\((.+?)\)\s*\{/g, "if ($1):");
      بايثون = بايثون.replace(/\}\s*آخر\s*\{/g, "else:");
      بايثون = بايثون.replace(/\u0643\u0631\u0631 من (\d+) إلى (\d+)\s*\{/g, "for i in range($1, $2+1):");
      بايثون = بايثون.replace(/\}/g, "");
      let أسطر = بايثون.split("\n");
      let مسافة = "";
      let نتيجة = "";
      for (let سطر of أسطر) {
        سطر = سطر.trim();
        if (سطر.endsWith(":")) { نتيجة += مسافة + سطر + "\n"; مسافة += "    "; }
        else { نتيجة += مسافة + سطر + "\n"; }
      }
      const بايثون_جاهز = await جاهز;
      try {
        await بايثون_جاهز.runPythonAsync(`\n${نتيجة}`);
        document.getElementById("الناتج").innerText = "✅ تم التنفيذ بنجاح";
      } catch (خطأ) {
        document.getElementById("الناتج").innerText = "❌ خطأ: " + خطأ;
      }
    }
    function احفظ() {
      const كود = document.getElementById("كود_عين").value;
      const ملف = new Blob([كود], { type: "text/plain" });
      const رابط = document.createElement("a");
      رابط.href = URL.createObjectURL(ملف);
      رابط.download = "الكود.ain";
      رابط.click();
    }
    </script>
    </body>
    </html>
    """, height=400, scrolling=True)

# ================================
# 4. الشريط الجانبي
# ================================
with st.sidebar:
    st.markdown("### 💬 نبراس")
    if st.button("➕ محادثة جديدة", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": "أنت نبراس، صديق ذكي ودود."},
            {"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}
        ]
        st.rerun()
    st.markdown("### 📋 المحادثات السابقة")
    if st.session_state.chat_history:
        for i, chat in enumerate(st.session_state.chat_history[::-1]):
            if st.button(f"💬 محادثة {i+1}", key=f"side_{i}"):
                st.session_state.messages = chat
                st.rerun()
    else:
        st.info("لا توجد محادثات")
    st.markdown("---")
    with st.expander("🧠 مترجم لغة عين", expanded=False):
        عين_مترجم()

# ================================
# 5. CSS
# ================================
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #f7f7f8; }
.chat-container { max-width: 750px; margin: 20px auto; padding: 0 20px; }
.msg-user { padding: 10px 16px; margin: 4px 0 8px auto; background: #e9ecef; border-radius: 18px; max-width: 80%; width: fit-content; }
.msg-bot { padding: 10px 16px; margin: 4px auto 8px 0; background: #ffffff; border-radius: 18px; max-width: 80%; width: fit-content; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.stChatInput { border-radius: 30px !important; border: 1px solid #e5e5e5 !important; background: #ffffff !important; padding: 2px 12px !important; position: fixed !important; bottom: 20px !important; left: 50% !important; transform: translateX(-50%) !important; width: 750px !important; max-width: 92% !important; z-index: 999 !important; }
.stChatInput input { border-radius: 30px !important; padding: 12px 16px !important; font-size: 15px !important; }
.stChatInput button { background: #1a1a1a !important; border-radius: 50% !important; padding: 4px 12px !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ================================
# 6. عرض المحادثة
# ================================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-bot">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ================================
# 7. أيقونة ولد (زر يعمل) فوق مربع الكتابة
# ================================
col1, col2, col3 = st.columns([1, 10, 1])
with col1:
    if st.button("👦", key="boy_icon", help="اضغط هنا"):
        st.info("🌟 مرحباً! أنا نبراس، كيف يمكنني مساعدتك؟")

# ================================
# 8. مربع الإدخال
# ================================
prompt = st.chat_input("اكتب سؤالك هنا...", key="main_chat")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("نبراس يفكر..."):
            try:
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=st.session_state.messages,
                    tools=[{"type": "web_search"}],
                    max_output_tokens=500
                )
                reply = response.output_text
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.session_state.chat_history.append(st.session_state.messages.copy())
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ خطأ: {str(e)}")
