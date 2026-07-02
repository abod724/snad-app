st.markdown("""
<style>

/* إخفاء عناصر Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* الخلفية */
.stApp {
    background: #ffffff;
}

/* الشريط العلوي */
.topbar {
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:10px 5px;
    margin-bottom:15px;
}

.left-icons, .right-icons {
    display:flex;
    gap:10px;
}

.icon-btn {
    background:#f3f4f6;
    border-radius:12px;
    padding:8px 12px;
    font-size:18px;
    border:1px solid #e5e7eb;
}

/* عنوان نبراس */
.title {
    text-align:center;
    font-size:34px;
    font-weight:bold;
    color:#111827;
    margin-top:10px;
    margin-bottom:25px;
}

/* رسائل المحادثة */
.chat-card {
    background:#f8fafc;
    border:1px solid #e5e7eb;
    border-radius:18px;
    padding:15px;
    margin-bottom:12px;
}

.user-card {
    border-right:4px solid #2563eb;
}

.ai-card {
    border-right:4px solid #10b981;
}

/* صندوق الإدخال */
.chat-input-box {
    position:fixed;
    bottom:20px;
    left:50%;
    transform:translateX(-50%);
    width:80%;
    background:white;
    border:1px solid #d1d5db;
    border-radius:28px;
    padding:12px;
    box-shadow:0 2px 12px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)
