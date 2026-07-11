import streamlit as st
from openai import OpenAI
import os

st.set_page_config(page_title="نبراس", layout="centered")
st.title("💬 نبراس")

# ===== استدعاء المفتاح من الأسرار =====
API_KEY = st.secrets.get("OPENAI_API_KEY")

if not API_KEY:
    st.error("🔴 مفتاح OpenAI غير مضاف في الأسرار")
    st.stop()

client = OpenAI(api_key=API_KEY)

# بدء المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "مرحباً، أنا نبراس. كيف يمكنني مساعدتك؟"}]

# عرض المحادثة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# مربع الإدخال
if prompt := st.chat_input("اكتب سؤالك..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("نبراس يفكر..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "أنت نبراس، صديق ذكي ودود."},
                        *st.session_state.messages
                    ],
                    max_tokens=500
                )
                reply = response.choices[0].message.content
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"⚠️ خطأ: {str(e)}")
