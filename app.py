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

def clean_reply_from_links(reply):
    reply = re.sub(r'https?://\S+|www\.\S+', '', reply)
    common_domains = r'\((?:[a-zA-Z0-9-]+\.)+(?:com|net|org|sa|gov|edu|me|news|tv|io|co)\)'
    reply = re.sub(common_domains, '', reply)
    reply = re.sub(r'\s(?:[a-zA-Z0-9-]+\.)+(?:com|net|org|sa|gov|edu|me|news|tv|io|co)[\.،,]?', '', reply)
    reply = re.sub(r'\s{2,}', ' ', reply)
    reply = re.sub(r'[،.]\s*[،.]', '،', reply)
    return reply.strip()
