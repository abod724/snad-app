from flask import Flask, request, jsonify
from openai import OpenAI
import os

# ─── المفتاح من الأسرار (اقرأ من ملف .streamlit/secrets.toml) ───
def get_secret(key):
    try:
        import tomllib
        with open(".streamlit/secrets.toml", "rb") as f:
            return tomllib.load(f).get(key)
    except:
        return os.getenv(key)

API_KEY = get_secret("OPENAI_API_KEY")
if not API_KEY:
    raise Exception("❌ مفتاح OpenAI غير موجود")

client = OpenAI(api_key=API_KEY)
app = Flask(__name__)

# ─── واجهة HTML (مضمنة) ───
HTML_PAGE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>نبراس</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #fff; color: #111; height: 100vh; display: flex; flex-direction: column; }
    header { background: #000; color: #fff; padding: 14px 24px; display: flex; align-items: center; gap: 12px; }
    header h1 { font-size: 18px; font-weight: 600; }
    .status { margin-right: auto; display: flex; align-items: center; gap: 6px; font-size: 13px; color: #aaa; }
    .dot { width: 8px; height: 8px; background: #4ade80; border-radius: 50%; animation: pulse 2s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
    .chat-area { flex: 1; overflow-y: auto; padding: 24px 20px; display: flex; flex-direction: column; gap: 16px; }
    .msg { display: flex; gap: 10px; max-width: 75%; animation: fadeIn .3s ease; }
    .msg.user { align-self: flex-start; flex-direction: row-reverse; }
    .msg.ai { align-self: flex-end; }
    @keyframes fadeIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
    .avatar { width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: bold; flex-shrink: 0; }
    .msg.user .avatar { background: #000; color: #fff; }
    .msg.ai .avatar { background: #f0f0f0; color: #000; border: 1px solid #ddd; }
    .bubble { padding: 12px 16px; border-radius: 18px; font-size: 15px; line-height: 1.6; word-wrap: break-word; }
    .msg.user .bubble { background: #000; color: #fff; border-bottom-right-radius: 4px; }
    .msg.ai .bubble { background: #f5f5f5; color: #111; border-bottom-left-radius: 4px; border: 1px solid #e5e5e5; }
    .typing .bubble { display: flex; gap: 5px; align-items: center; padding: 14px 18px; }
    .typing .bubble span { width: 8px; height: 8px; background: #999; border-radius: 50%; animation: bounce 1.2s infinite; }
    .typing .bubble span:nth-child(2){animation-delay:.2s}
    .typing .bubble span:nth-child(3){animation-delay:.4s}
    @keyframes bounce { 0%,80%,100%{transform:translateY(0)} 40%{transform:translateY(-6px)} }
    .input-bar { background: #fff; border-top: 1px solid #e8e8e8; padding: 14px 16px; }
    #img-previews { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }
    .thumb-wrap { position: relative; }
    .thumb-wrap img { width: 56px; height: 56px; object-fit: cover; border-radius: 8px; border: 1px solid #ddd; }
    .thumb-wrap button { position: absolute; top: -6px; right: -6px; background: #000; color: #fff; border: none; border-radius: 50%; width: 18px; height: 18px; font-size: 11px; cursor: pointer; }
    .input-row { display: flex; align-items: center; gap: 10px; background: #f9f9f9; border: 1.5px solid #ddd; border-radius: 16px; padding: 8px 12px; transition: border-color .2s; }
    .input-row:focus-within { border-color: #000; }
    .icon-btn { background: none; border: none; cursor: pointer; padding: 4px; display: flex; align-items: center; color: #555; border-radius: 8px; transition: background .2s; }
    .icon-btn:hover { background: #eee; color: #000; }
    #userInput { flex: 1; border: none; background: transparent; outline: none; font-size: 15px; color: #111; resize: none; min-height: 24px; max-height: 120px; font-family: inherit; }
    #userInput::placeholder { color: #aaa; }
    .send-btn { background: #000; color: #fff; border: none; border-radius: 12px; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; cursor: pointer; flex-shrink: 0; transition: transform .15s, background .2s; }
    .send-btn:hover { background: #333; transform: scale(1.05); }
    .send-btn:disabled { background: #ccc; cursor: not-allowed; transform: none; }
    #recording-indicator { display: none; align-items: center; gap: 8px; color: #e00; font-size: 13px; margin-top: 6px; }
    .rec-dot { width: 8px; height: 8px; background: red; border-radius: 50%; animation: pulse 1s infinite; }
    .img-in-chat { max-width: 200px; border-radius: 12px; margin-top: 6px; border: 1px solid #e0e0e0; }
  </style>
</head>
<body>
<header>
  <div style="width:36px;height:36px;background:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;">
    <svg viewBox="0 0 24 24" width="20" fill="none" stroke="#000" stroke-width="2">
      <circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/>
    </svg>
  </div>
  <h1>نبراس</h1>
  <div class="status"><div class="dot"></div><span>متصل</span></div>
</header>

<div class="chat-area" id="chatArea">
  <div class="msg ai">
    <div class="avatar">🤖</div>
    <div class="bubble">مرحباً! أنا نبراس، مساعدك الذكي. كيف أقدر أساعدك اليوم؟ 😊</div>
  </div>
</div>

<div class="input-bar">
  <div id="img-previews"></div>
  <div class="input-row">
    <label class="icon-btn" title="رفع صورة">
      <input type="file" id="imgInput" accept="image/*" multiple hidden/>
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="8.5" r="1.5"/>
        <path d="M21 15l-5-5L5 21"/>
      </svg>
    </label>
    <button class="icon-btn" id="micBtn" title="تسجيل صوتي">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10a7 7 0 0014 0"/><line x1="12" y1="19" x2="12" y2="22"/>
      </svg>
    </button>
    <textarea id="userInput" placeholder="اكتب رسالتك هنا..." rows="1"></textarea>
    <button class="send-btn" id="sendBtn" title="إرسال">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
      </svg>
    </button>
  </div>
  <div id="recording-indicator"><div class="rec-dot"></div><span>جاري التسجيل...</span></div>
</div>

<script>
const chatArea = document.getElementById('chatArea');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const imgInput = document.getElementById('imgInput');
const imgPreviews = document.getElementById('img-previews');
const micBtn = document.getElementById('micBtn');
const recIndicator = document.getElementById('recording-indicator');

let pendingImages = [];
let isRecording = false;
let recognition = null;

userInput.addEventListener('input', () => {
  userInput.style.height = 'auto';
  userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
});
userInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});
sendBtn.addEventListener('click', sendMessage);

imgInput.addEventListener('change', () => {
  Array.from(imgInput.files).forEach(file => {
    const reader = new FileReader();
    reader.onload = e => {
      pendingImages.push(e.target.result);
      const wrap = document.createElement('div');
      wrap.className = 'thumb-wrap';
      wrap.innerHTML = `<img src="${e.target.result}"/><button onclick="this.parentNode.remove();pendingImages.splice(${pendingImages.length-1},1)">×</button>`;
      imgPreviews.appendChild(wrap);
    };
    reader.readAsDataURL(file);
  });
  imgInput.value = '';
});

micBtn.addEventListener('click', () => {
  if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
    alert('المتصفح لا يدعم التسجيل الصوتي. استخدم Chrome.');
    return;
  }
  if (isRecording) {
    recognition && recognition.stop();
    isRecording = false;
    recIndicator.style.display = 'none';
    micBtn.style.color = '';
    return;
  }
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SR();
  recognition.lang = 'ar-SA';
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.onresult = e => {
    userInput.value += e.results[0][0].transcript + ' ';
    userInput.dispatchEvent(new Event('input'));
  };
  recognition.onend = () => {
    isRecording = false;
    recIndicator.style.display = 'none';
    micBtn.style.color = '';
  };
  recognition.start();
  isRecording = true;
  recIndicator.style.display = 'flex';
  micBtn.style.color = 'red';
});

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text && pendingImages.length === 0) return;

  const userDiv = document.createElement('div');
  userDiv.className = 'msg user';
  let imgHTML = pendingImages.map(src => `<img class="img-in-chat" src="${src}"/>`).join('');
  userDiv.innerHTML = `<div class="avatar">أنت</div><div class="bubble">${text ? escapeHtml(text) : ''}${imgHTML}</div>`;
  chatArea.appendChild(userDiv);

  const images = pendingImages;
  userInput.value = ''; userInput.style.height = 'auto';
  pendingImages = []; imgPreviews.innerHTML = '';
  sendBtn.disabled = true;
  scrollBottom();

  const typing = document.createElement('div');
  typing.className = 'msg ai typing';
  typing.innerHTML = `<div class="avatar">🤖</div><div class="bubble"><span></span><span></span><span></span></div>`;
  chatArea.appendChild(typing);
  scrollBottom();

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        images: images.map(img => img.split(',')[1])
      })
    });
    const data = await response.json();
    typing.remove();
    const aiDiv = document.createElement('div');
    aiDiv.className = 'msg ai';
    aiDiv.innerHTML = `<div class="avatar">🤖</div><div class="bubble">${data.reply || '⚠️ خطأ في الرد'}</div>`;
    chatArea.appendChild(aiDiv);
  } catch (error) {
    typing.remove();
    const aiDiv = document.createElement('div');
    aiDiv.className = 'msg ai';
    aiDiv.innerHTML = `<div class="avatar">🤖</div><div class="bubble">⚠️ تعذر الاتصال بالخادم</div>`;
    chatArea.appendChild(aiDiv);
  }
  sendBtn.disabled = false;
  scrollBottom();
}
function scrollBottom() { chatArea.scrollTo({ top: chatArea.scrollHeight, behavior: 'smooth' }); }
function escapeHtml(str) { return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
</script>
</body>
</html>"""

@app.route("/")
def index():
    return HTML_PAGE

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()
    images = data.get("images", [])

    try:
        messages = [{"role": "system", "content": "أنت نبراس، مساعد ذكي ودود."}]
        if images:
            content = [{"type": "text", "text": user_message or "صف هذه الصورة"}]
            for img in images[:3]:
                content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})
            messages.append({"role": "user", "content": content})
            resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages, max_tokens=800)
        else:
            messages.append({"role": "user", "content": user_message or "مرحباً"})
            resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages, max_tokens=800)
        return jsonify({"reply": resp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"⚠️ خطأ: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
