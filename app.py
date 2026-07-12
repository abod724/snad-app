import streamlit as st
from openai import OpenAI
from googlesearch import search as google_search
import base64

st.set_page_config(page_title="نبراس", page_icon="🤖", layout="wide")

API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير موجود")
    st.stop()

# ─── CSS بسيط ───
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #ffffff; }
[data-testid="stChatMessage"] { max-width: 760px; margin: 0 auto; padding: 8px 0; }
[data-testid="stChatMessageContent"] { font-size: 16px; line-height: 1.75; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background: #f7f7f8; border-radius: 12px; padding: 14px 18px; }
</style>
""", unsafe_allow_html=True)

# ─── الشريط الجانبي ───
with st.sidebar:
    if st.button("➕ محادثة جديدة", use_container_width=True):
        st.session_state.messages = []
        st.session_state.sources = []
        st.rerun()
    
    model = st.selectbox("النموذج", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"])
    temperature = st.slider("الإبداع", 0.0, 2.0, 0.7, 0.1)
    web_search = st.toggle("بحث قوقل", value=True)
    system_prompt = st.text_area("تعليمات النظام", value="أنت نبراس، مساعد ذكي محترف.", height=80)

# ─── دوال مساعدة ───
def search_google(query):
    try:
        results = list(google_search(query, num_results=3, advanced=True))
        if not results:
            return None, []
        context, sources = [], []
        for i, r in enumerate(results, 1):
            context.append(f"[{i}] {getattr(r,'title','')}\n{getattr(r,'description','')}\nالرابط: {getattr(r,'url','')}")
            sources.append({"title": getattr(r,'title',''), "url": getattr(r,'url','')})
        return "\n\n".join(context), sources
    except:
        return None, []

def image_to_base64(file):
    return base64.b64encode(file.getvalue()).decode()

# ─── تهيئة الجلسة ───
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources" not in st.session_state:
    st.session_state.sources = []

# ─── عرض المحادثة ───
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and i < len(st.session_state.sources) and st.session_state.sources[i]:
            links = "".join(f'<a href__="{s["url"]}" target="_blank" style="margin:2px;display:inline-block;background:#f0f0f0;padding:2px 10px;border-radius:6px;font-size:13px;color:#2563eb;text-decoration:none;">🔗 {s["title"][:40]}</a>' for s in st.session_state.sources[i])
            st.markdown(f"**المصادر:**<br>{links}", unsafe_allow_html=True)

# ─── ترحيب ───
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown("أهلاً 👋 أنا نبراس، كيف أساعدك؟")

# ─── الإدخال ───
uploaded_image = st.file_uploader("📷", type=["png", "jpg", "jpeg"], label_visibility="collapsed", key="img")
prompt = st.chat_input("اكتب رسالتك...")

if prompt:
    user_text = prompt
    if uploaded_image:
        user_text = prompt or "اشرح هذه الصورة"
    
    # ─── عرض رسالة المستخدم ───
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_text)
    
    # ─── حفظ رسالة المستخدم ───
    st.session_state.messages.append({"role": "user", "content": user_text})
    
    # ─── رد المساعد ───
    with st.chat_message("assistant", avatar="🤖"):
        try:
            client = OpenAI(api_key=API_KEY)
            
            # بحث
            search_context, sources = None, []
            if web_search and not uploaded_image:
                search_context, sources = search_google(user_text)
            
            # بناء الرسائل
            msgs = [{"role": "system", "content": system_prompt}]
            if search_context:
                msgs.append({"role": "system", "content": f"نتائج البحث:\n{search_context}"})
            
            if uploaded_image:
                b64 = image_to_base64(uploaded_image)
                msgs.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]
                })
            else:
                msgs.extend(st.session_state.messages[-8:])
            
            # ─── Streaming ───
            stream = client.chat.completions.create(
                model=model,
                messages=msgs,
                temperature=temperature,
                stream=True,
                max_tokens=2048
            )
            
            # جمع الرد
            response = st.write_stream(stream)
            
            # حفظ الرد والمصادر
            st.session_state.messages.append({"role": "assistant", "content": response})
            while len(st.session_state.sources) < len(st.session_state.messages):
                st.session_state.sources.append([])
            st.session_state.sources[-1] = sources
            
            # عرض المصادر
            if sources:
                links = "".join(f'<a href__="{s["url"]}" target="_blank" style="margin:2px;display:inline-block;background:#f0f0f0;padding:2px 10px;border-radius:6px;font-size:13px;color:#2563eb;text-decoration:none;">🔗 {s["title"][:40]}</a>' for s in sources)
                st.markdown(f"**المصادر:**<br>{links}", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ {str(e)}")
