from styling import template2_page_style
import streamlit as st
from openai import OpenAI
import base64
from datetime import datetime
import re
import json
import os

# ============================================================
# 1. المفتاح والعميل
# ============================================================
API_KEY = st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير مضاف")
    st.stop()
client = OpenAI(api_key=API_KEY)

# ============================================================
# 2. الذاكرة الدائمة
# ============================================================
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}]

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "sessions" not in st.session_state:
    st.session_state.sessions = []

memory = load_memory()

# ============================================================
# 3. دوال المساعدة
# ============================================================
def chat_with_nbras(messages, question, uploaded_images=None):
    """ترسل السؤال إلى OpenAI وتعرض الرد"""
    messages.append({"role": "user", "content": question})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)
    
    # عرض الصور المرفوعة
    if uploaded_images:
        for img in uploaded_images:
            st.image(f"data:image/png;base64,{img['data']}", width=250)
    
    with st.spinner("نبراس يفكر..."):
        try:
            # بحث ويب محدث
            search_results = ""
            try:
                search_response = client.responses.create(
                    model="gpt-4o-mini",
                    input=[{"role": "user", "content": f"ابحث عن: {question}"}],
                    tools=[{"type": "web_search"}],
                    max_output_tokens=300
                )
                search_results = search_response.output_text
            except:
                pass
            
            system_prompt = f"""
            أنت نبراس، صديق ذكي ودود.
            - تحدث بأسلوب بسيط، بدون أيقونات.
            - استخدم اسم المستخدم: {st.session_state.user_name if st.session_state.user_name else "لم أعرفه"}
            - اعتمد على المعلومات التالية من البحث:
            {search_results if search_results else "لا توجد نتائج بحث محدثة."}
            """
            
            messages_list = [
                {"role": "system", "content": system_prompt},
                *[{"role": m["role"], "content": m["content"]} for m in messages[:-1]]
            ]
            
            if uploaded_images:
                messages_list.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{uploaded_images[0]['data']}"}}
                    ]
                })
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages_list,
                    max_tokens=600
                )
            else:
                messages_list.append({"role": "user", "content": question})
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages_list,
                    max_tokens=600
                )
            
            answer = response.choices[0].message.content
            messages.append({"role": "assistant", "content": answer})
            
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(answer)
            
            # حفظ الجلسة
            st.session_state.sessions.append({
                "date": datetime.now().strftime("%H:%M - %d/%m"),
                "messages": messages.copy()
            })
            
            # تشغيل الصوت تلقائياً
            try:
                speech = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=answer[:300],
                    response_format="mp3"
                )
                audio_b64 = base64.b64encode(speech.content).decode("utf-8")
                st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")
            except:
                pass
            
        except Exception as e:
            st.error(f"⚠️ خطأ: {str(e)}")

def clear_session():
    """يمسح المحادثة ويبدأ جلسة جديدة"""
    st.cache_data.clear()
    st.session_state.messages = [{"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}]
    st.session_state.sessions = []
    st.success("✅ تم بدء محادثة جديدة")

# ============================================================
# 4. الواجهة الرئيسية
# ============================================================
def main():
    # تطبيق تنسيق القالب
    template2_page_style()
    
    st.title('نبراس - صديقك الذكي')
    
    # الشريط الجانبي
    with st.sidebar:
        st.markdown("### 💬 نبراس")
        st.markdown("---")
        
        if st.button("➕ محادثة جديدة", use_container_width=True):
            clear_session()
            st.rerun()
        
        st.markdown("### 📋 المحادثات السابقة")
        if st.session_state.sessions:
            for i, s in enumerate(st.session_state.sessions[::-1]):
                if st.button(f"💬 {s['date']}", key=f"side_{i}", use_container_width=True):
                    st.session_state.messages = s["messages"]
                    st.rerun()
        else:
            st.info("لا توجد محادثات سابقة")
        
        st.markdown("---")
        st.markdown("### 🎤 الصوت")
        if st.button("🔊 تشغيل آخر رد", use_container_width=True):
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
                last_reply = st.session_state.messages[-1]["content"]
                try:
                    speech = client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=last_reply[:300],
                        response_format="mp3"
                    )
                    audio_b64 = base64.b64encode(speech.content).decode("utf-8")
                    st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")
                except:
                    st.warning("⚠️ تعذر تشغيل الصوت")
            else:
                st.warning("⚠️ لا يوجد رد سابق")
    
    # عرض المحادثة السابقة
    avatars = {
        "assistant": "🤖",
        "user": "👤"
    }
    
    for message in st.session_state.messages:
        avatar = avatars.get(message["role"], "❓")
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message['content'])
    
    # استخراج اسم المستخدم
    if st.session_state.user_name is None:
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            last_msg = st.session_state.messages[-1]["content"]
            match = re.search(r"اسمي\s+(\w+)", last_msg)
            if match:
                st.session_state.user_name = match.group(1)
                if st.session_state.user_name not in memory["users"]:
                    memory["users"][st.session_state.user_name] = {"first_seen": datetime.now().isoformat()}
                    save_memory(memory)
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"أهلاً {st.session_state.user_name}! سعيد برؤيتك 🤍"}
                )
                st.rerun()
    
    # مربع الإدخال
    question = st.chat_input(
        "اكتب سؤالك... أو ارفع صورة",
        accept_file=True,
        file_type=["jpg", "jpeg", "png", "gif", "webp"]
    )
    
    # معالجة الإدخال
    if question:
        query = question.text.strip() if hasattr(question, 'text') else str(question).strip()
        
        # معالجة الصور المرفوعة
        uploaded_images = []
        if hasattr(question, 'files') and question.files:
            for file in question.files:
                try:
                    img_bytes = file.getvalue()
                    img_b64 = base64.b64encode(img_bytes).decode()
                    uploaded_images.append({"name": file.name, "data": img_b64})
                except:
                    pass
        
        if query or uploaded_images:
            user_message = query
            if uploaded_images:
                if query:
                    user_message += f"\n📷 صورة: {uploaded_images[0]['name']}"
                else:
                    user_message = f"📷 صورة: {uploaded_images[0]['name']}"
            
            chat_with_nbras(st.session_state.messages, user_message, uploaded_images)
            
            # حفظ في الذاكرة الدائمة
            if st.session_state.user_name and st.session_state.user_name in memory["users"]:
                memory["users"][st.session_state.user_name]["last_seen"] = datetime.now().isoformat()
                save_memory(memory)

if __name__ == "__main__":
    main()
