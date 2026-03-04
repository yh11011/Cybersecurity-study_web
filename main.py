"""
CyberLearn — 防禦型資安學習平台
Phase 1 MVP（題庫 + 說明模式，AI 功能待未來加入）
"""

import asyncio
import json
import random
import re
import smtplib
import string
import time
from collections import defaultdict
from datetime import datetime, timezone
from email.mime.text import MIMEText
from typing import Optional

import os

import aiosqlite
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ─── Config ──────────────────────────────────────────────────────────────────

DB_PATH = "cyberlearn.db"

# SMTP (Gmail) for password reset
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "h11.bot.vn@gmail.com")
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "elhz esdn bamh jwpw")
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

ph = PasswordHasher()
app = FastAPI(title="CyberLearn API — Quiz Mode")

# CORS — 允許 GitHub Pages 前端跨域存取
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://cybersecurity.nex11.me,https://yh11011.github.io").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Lesson data (Phase 1: 關卡 1 only) ─────────────────────────────────────

LESSONS = {
    "password_strength": {
        "id": "password_strength",
        "title": "密碼強度",
        "emoji": "🔐",
        "subtitle": "你用貓咪名字當密碼，駭客怎麼猜到的？",
        "topic": "密碼強度與字典攻擊",
        "objective": "讓使用者了解弱密碼的危險，學會設定強密碼",
        "trap": {
            "type": "password_meter",
            "description": "密碼強度計顯示「強」但實際上很弱",
        },
        "layers": [1],  # Phase 1 only layer 1
        "xp": 100,
        "badge": "🛡️ 密碼衛士",
    },
    "phishing": {
        "id": "phishing",
        "title": "釣魚郵件",
        "emoji": "🎣",
        "subtitle": "你收到 Costco 抽到 iPhone，你點了嗎？",
        "topic": "釣魚郵件辨識",
        "objective": "讓使用者學會辨識釣魚郵件的特徵",
        "locked": True,
        "xp": 100,
        "badge": "🔍 郵件偵探",
    },
    "social_engineering": {
        "id": "social_engineering",
        "title": "社交工程",
        "emoji": "🎭",
        "subtitle": "陌生人問你生日+學校，他在幹嘛？",
        "topic": "社交工程攻擊",
        "objective": "讓使用者了解社交工程的手法與防禦",
        "locked": True,
        "xp": 100,
        "badge": "🧠 心理防禦師",
    },
    "public_wifi": {
        "id": "public_wifi",
        "title": "公共 WiFi",
        "emoji": "📡",
        "subtitle": "咖啡廳 WiFi 輸入網銀密碼的後果",
        "topic": "公共 WiFi 風險",
        "objective": "讓使用者了解中間人攻擊與 HTTPS 的重要性",
        "locked": True,
        "xp": 100,
        "badge": "📡 網路衛士",
    },
    "two_factor": {
        "id": "two_factor",
        "title": "雙因素驗證",
        "emoji": "🔑",
        "subtitle": "為什麼密碼洩漏了還沒事？",
        "topic": "雙因素驗證 (2FA)",
        "objective": "讓使用者了解 2FA 的重要性與運作原理",
        "locked": True,
        "xp": 100,
        "badge": "🔑 雙重守門人",
    },
}

# ─── Questions (Phase 1 — 關卡 1) ────────────────────────────────────────────

QUESTIONS_DATA = [
    {
        "id": 1,
        "topic": "password_strength",
        "difficulty": 1,
        "layer": 1,
        "tags": ["dictionary_attack", "weak_password"],
        "question": "你設定密碼 'Whiskers2005'（你的貓咪名字+出生年），這個密碼主要的問題是什麼？",
        "options": [
            "A. 密碼太短，不到 8 個字元",
            "B. 包含個人資訊，可以用字典攻擊猜到",
            "C. 沒有包含特殊符號",
            "D. 沒有包含大寫字母",
        ],
        "answer": "B",
        "explanation": "字典攻擊會用真實的名字、寵物名稱、年份組合來嘗試。'Whiskers2005' 雖然看起來複雜，但駭客的字典裡就有這種模式！真正安全的密碼要用隨機字元，或是密碼管理器產生的長密碼。",
        "hint": "想想看，什麼密碼是「機器猜不到」的？",
    },
    {
        "id": 2,
        "topic": "password_strength",
        "difficulty": 1,
        "layer": 1,
        "tags": ["password_reuse", "breach"],
        "question": "同一個密碼用在 10 個不同網站，最主要的風險是什麼？",
        "options": [
            "A. 密碼會自動過期失效",
            "B. 只要其中一個網站外洩，所有帳號都危險",
            "C. 瀏覽器記不住這麼多",
            "D. 密碼輸入次數太多容易被看到",
        ],
        "answer": "B",
        "explanation": "這叫做「密碼填充攻擊」（Credential Stuffing）。駭客拿到一個網站外洩的帳密後，會自動嘗試登入其他網站。如果你每個地方都用同一組，中獎機率大大提高！",
        "hint": "想想雞蛋不要放在同一個籃子裡的道理",
    },
    {
        "id": 3,
        "topic": "password_strength",
        "difficulty": 1,
        "layer": 1,
        "tags": ["strong_password", "best_practice"],
        "question": "下列哪個密碼最安全？",
        "options": [
            "A. P@ssw0rd123",
            "B. 我愛台灣2024",
            "C. xK#9mQ$vL2nP",
            "D. password（全小寫）",
        ],
        "answer": "C",
        "explanation": "C 是隨機字元組合，沒有任何規律可循。A 看起來複雜但是常見的「字典詞+替換」模式；B 使用有意義的詞語；D 是最常見的弱密碼之一。真正的強密碼是「你自己也記不住的那種」——這就是密碼管理器存在的原因！",
        "hint": "越難記住的密碼，通常越安全",
    },
    # ── 關卡 2: 釣魚郵件 ──
    {
        "id": 4,
        "topic": "phishing",
        "difficulty": 1,
        "layer": 1,
        "tags": ["phishing_email", "url_check"],
        "question": "你收到一封來自 'service@amaz0n-security.com' 的信，說你的帳號被盜，需要立即點連結驗證。你應該怎麼做？",
        "options": [
            "A. 立刻點連結，保護帳號最重要",
            "B. 檢查寄件者地址，發現 'amaz0n' 是零不是 o，判斷為釣魚郵件",
            "C. 回覆郵件詢問是否為真",
            "D. 轉發給朋友幫忙確認",
        ],
        "answer": "B",
        "explanation": "釣魚郵件最常見的手法就是偽造看似正規的寄件者地址。'amaz0n' 把 o 換成 0，不仔細看很容易上當。正確做法是直接到官方網站檢查帳號狀態，而不是點郵件中的連結。",
        "hint": "仔細看寄件者的 Email 地址，有沒有奇怪的拼寫？",
    },
    {
        "id": 5,
        "topic": "phishing",
        "difficulty": 1,
        "layer": 1,
        "tags": ["phishing_urgency", "social_trick"],
        "question": "釣魚郵件最常用的心理戰術是什麼？",
        "options": [
            "A. 用很長的文字讓你懶得看",
            "B. 製造緊急感，讓你來不及思考就行動",
            "C. 用很多技術術語讓你覺得很專業",
            "D. 附上很多附件讓你好奇打開",
        ],
        "answer": "B",
        "explanation": "「你的帳號將在 24 小時內被停用！」「立即行動否則⋯⋯」——這些都是釣魚郵件的經典話術。製造恐慌和緊急感，讓你來不及冷靜判斷就點了連結。記住：正規公司不會用威脅語氣要求你立即操作。",
        "hint": "想想看，正規公司會用什麼語氣跟你溝通？",
    },
    {
        "id": 6,
        "topic": "phishing",
        "difficulty": 1,
        "layer": 1,
        "tags": ["phishing_link", "url_safety"],
        "question": "你收到朋友傳的「免費 Netflix 帳號」連結，網址是 netflix-free-premium.xyz。這最可能是什麼？",
        "options": [
            "A. Netflix 的官方促銷活動",
            "B. 釣魚網站，想騙你輸入帳密或個資",
            "C. 朋友自己架設的分享平台",
            "D. Netflix 合作夥伴的優惠",
        ],
        "answer": "B",
        "explanation": "正規的 Netflix 網址是 netflix.com，不會用 .xyz 這種便宜的網域。「免費帳號」本身就是誘餌，目的是讓你在假網站輸入帳號密碼。即使是朋友傳的連結，也可能是朋友的帳號被盜後自動發送的。",
        "hint": "檢查網址的網域名稱，是不是官方的？",
    },
    # ── 關卡 3: 社交工程 ──
    {
        "id": 7,
        "topic": "social_engineering",
        "difficulty": 1,
        "layer": 1,
        "tags": ["personal_info", "pretexting"],
        "question": "一個自稱是「學校行政人員」的陌生人打電話來，要求你提供學號、生日和身分證末四碼來「核對身份」。你應該怎麼做？",
        "options": [
            "A. 對方聽起來很專業，直接提供資訊",
            "B. 先掛電話，自己打學校官方電話確認",
            "C. 只提供學號，其他不說",
            "D. 請對方發 Email 來處理",
        ],
        "answer": "B",
        "explanation": "這是典型的「假冒身份」（Pretexting）社交工程攻擊。攻擊者會假裝是你信任的機構人員來套取個資。正確做法是掛斷電話，自己主動撥打官方號碼確認。永遠不要在被動接到的電話中提供敏感資訊。",
        "hint": "誰發起的通訊很重要——是你主動聯繫，還是對方找上你？",
    },
    {
        "id": 8,
        "topic": "social_engineering",
        "difficulty": 1,
        "layer": 1,
        "tags": ["social_media", "oversharing"],
        "question": "你在 Instagram 發了生日蛋糕照片，標記了學校和寵物名字。這些資訊可能被怎麼利用？",
        "options": [
            "A. 沒什麼風險，大家都這樣發",
            "B. 駭客可以用這些資訊猜你的密碼或安全問題答案",
            "C. 只有朋友看得到，不用擔心",
            "D. Instagram 會保護你的隱私",
        ],
        "answer": "B",
        "explanation": "生日、學校名稱、寵物名字——這些全都是常見的密碼組成元素和「忘記密碼」安全問題的答案！駭客會從社群媒體蒐集這些公開資訊來推測你的密碼。這就是為什麼不該用個人資訊當密碼，也要注意社群隱私設定。",
        "hint": "回想一下你的密碼和安全問題，有用到這些資訊嗎？",
    },
    {
        "id": 9,
        "topic": "social_engineering",
        "difficulty": 1,
        "layer": 1,
        "tags": ["tailgating", "physical_security"],
        "question": "有人在公司大門口說「我忘帶員工證了，可以幫我刷一下嗎？」你應該怎麼做？",
        "options": [
            "A. 幫他刷卡，大家互相幫忙",
            "B. 禮貌拒絕，請他聯繫管理員或自己的主管",
            "C. 看他穿著像員工就幫他",
            "D. 讓他跟在你後面進去",
        ],
        "answer": "B",
        "explanation": "這叫做「尾隨」（Tailgating），是實體社交工程的常見手法。攻擊者利用人的禮貌和信任心理來繞過門禁系統。正確做法是禮貌但堅定地拒絕，引導對方走正規流程。不要因為對方看起來「像是員工」就放行。",
        "hint": "安全措施存在是有原因的——即使幫忙的出發點是好的",
    },
    # ── 關卡 4: 公共 WiFi ──
    {
        "id": 10,
        "topic": "public_wifi",
        "difficulty": 1,
        "layer": 1,
        "tags": ["mitm", "public_network"],
        "question": "你在咖啡廳連上免費 WiFi「CafeWiFi_Free」後登入網路銀行。這個行為最大的風險是什麼？",
        "options": [
            "A. WiFi 速度太慢，交易可能失敗",
            "B. 攻擊者可能架設假 WiFi，攔截你的帳密（中間人攻擊）",
            "C. 咖啡廳可能收取隱藏的上網費",
            "D. 其他客人可能偷看你的螢幕",
        ],
        "answer": "B",
        "explanation": "公共 WiFi 最大的風險是「中間人攻擊」（Man-in-the-Middle）。攻擊者可以架設同名的假 WiFi 熱點，一旦你連上，你所有的網路流量都會經過他。即使是真的公共 WiFi，未加密的流量也可能被同一網路上的人攔截。",
        "hint": "想想看，你怎麼確定這個 WiFi 真的是咖啡廳提供的？",
    },
    {
        "id": 11,
        "topic": "public_wifi",
        "difficulty": 1,
        "layer": 1,
        "tags": ["https", "encryption"],
        "question": "使用公共 WiFi 時，下列哪個做法最能保護你的資料？",
        "options": [
            "A. 只連有密碼的 WiFi",
            "B. 確認網站網址是 https:// 開頭（有鎖頭圖示）",
            "C. 開啟飛航模式",
            "D. 用無痕模式瀏覽",
        ],
        "answer": "B",
        "explanation": "HTTPS 會加密你和網站之間的通訊，即使有人攔截封包也看不到內容。有密碼的 WiFi 不代表安全（其他使用者仍可監聽）；無痕模式只是不記錄瀏覽紀錄，不會加密流量。最佳方案是 HTTPS + VPN 雙重保護。",
        "hint": "加密是防止被偷看的關鍵——什麼協議能加密你的網頁通訊？",
    },
    {
        "id": 12,
        "topic": "public_wifi",
        "difficulty": 1,
        "layer": 1,
        "tags": ["vpn", "best_practice"],
        "question": "你經常需要在外面工作，下列哪個是使用公共網路最安全的方式？",
        "options": [
            "A. 自帶手機熱點或使用 VPN",
            "B. 只在星巴克這種大品牌連 WiFi",
            "C. 每次換一個不同的 WiFi 連",
            "D. 登入前先清除瀏覽器 Cookie",
        ],
        "answer": "A",
        "explanation": "自帶手機熱點最安全，因為你完全控制網路環境。如果必須用公共 WiFi，VPN（虛擬私人網路）會加密所有流量，就像在公共道路上開了一條私人隧道。大品牌 WiFi 不一定更安全——攻擊者可以在任何地方架設假熱點。",
        "hint": "想想看，什麼方法能讓你在公共網路上也像在家一樣安全？",
    },
    # ── 關卡 5: 雙因素驗證 ──
    {
        "id": 13,
        "topic": "two_factor",
        "difficulty": 1,
        "layer": 1,
        "tags": ["2fa", "authentication"],
        "question": "什麼是雙因素驗證（2FA）？",
        "options": [
            "A. 用兩個不同的密碼登入",
            "B. 除了密碼外，還需要第二種方式驗證身份（如手機驗證碼）",
            "C. 兩個人一起確認才能登入",
            "D. 登入時需要輸入密碼兩次",
        ],
        "answer": "B",
        "explanation": "2FA 的「兩個因素」指的是：你知道的東西（密碼）+ 你擁有的東西（手機、硬體金鑰）或你本人的特徵（指紋、臉部辨識）。即使密碼被盜，沒有第二個因素攻擊者也無法登入。這是目前最有效的帳號保護方式之一。",
        "hint": "想想「因素」代表不同類型的驗證方式",
    },
    {
        "id": 14,
        "topic": "two_factor",
        "difficulty": 1,
        "layer": 1,
        "tags": ["2fa_methods", "security_comparison"],
        "question": "下列哪種 2FA 方式最安全？",
        "options": [
            "A. 簡訊驗證碼（SMS OTP）",
            "B. 硬體安全金鑰（如 YubiKey）",
            "C. Email 驗證碼",
            "D. 安全問題（你的寵物叫什麼？）",
        ],
        "answer": "B",
        "explanation": "硬體安全金鑰是最安全的 2FA 方式，因為它需要實體接觸，無法被遠端攻擊。簡訊可能被 SIM 卡劫持（SIM Swapping）攻擊；Email 可能被入侵；安全問題的答案通常可以從社群媒體猜到。Google 內部自從強制使用硬體金鑰後，釣魚攻擊成功率降為零。",
        "hint": "哪個方式需要你「實際拿在手上」才能用？",
    },
    {
        "id": 15,
        "topic": "two_factor",
        "difficulty": 1,
        "layer": 1,
        "tags": ["2fa_bypass", "phishing_2fa"],
        "question": "你開啟了 2FA，但收到釣魚網站要求你輸入驗證碼。如果你照做了，會發生什麼？",
        "options": [
            "A. 2FA 會保護你，不用擔心",
            "B. 攻擊者可以即時用你的驗證碼登入你的帳號",
            "C. 驗證碼會自動失效，不會有問題",
            "D. 網站會偵測到異常並阻擋",
        ],
        "answer": "B",
        "explanation": "這叫做「即時釣魚」（Real-time Phishing）。攻擊者在你輸入驗證碼的瞬間，把它轉發到真正的登入頁面。所以 2FA 不是萬能的——你仍然需要確認自己是在正確的網站上。這就是為什麼硬體金鑰比驗證碼更安全，因為它會驗證網站的真實性。",
        "hint": "驗證碼是有時效的，但如果攻擊者「馬上」就用呢？",
    },
]

# ─── Database setup ───────────────────────────────────────────────────────────

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT DEFAULT NULL,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                completed_lessons TEXT DEFAULT '[]',
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        # Add email column if upgrading from old schema
        try:
            await db.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT NULL")
        except Exception:
            pass
        await db.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                code TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                used INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY,
                topic TEXT NOT NULL,
                difficulty INTEGER NOT NULL,
                layer INTEGER NOT NULL,
                tags TEXT,
                question TEXT NOT NULL,
                options TEXT NOT NULL,
                answer TEXT NOT NULL,
                explanation TEXT NOT NULL,
                hint TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_knowledge (
                user_id INTEGER,
                topic TEXT,
                mastery_score REAL DEFAULT 0.0,
                last_practiced TEXT,
                attempt_count INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, topic)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS answer_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question_id INTEGER,
                is_correct INTEGER,
                time_spent_seconds INTEGER,
                answered_at TEXT DEFAULT (datetime('now'))
            )
        """)
        # Seed questions
        for q in QUESTIONS_DATA:
            await db.execute("""
                INSERT OR IGNORE INTO questions
                (id, topic, difficulty, layer, tags, question, options, answer, explanation, hint)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                q["id"], q["topic"], q["difficulty"], q["layer"],
                json.dumps(q["tags"], ensure_ascii=False),
                q["question"],
                json.dumps(q["options"], ensure_ascii=False),
                q["answer"], q["explanation"], q["hint"]
            ))
        await db.commit()

# ─── Pydantic models ──────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    nickname: str
    password: str

class LoginRequest(BaseModel):
    nickname: str
    password: str

class AnswerRequest(BaseModel):
    user_id: int
    question_id: int
    answer: str
    time_spent: int

class BindEmailRequest(BaseModel):
    user_id: int
    email: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str

# ─── Helpers ──────────────────────────────────────────────────────────────────

def xp_to_level(xp: int) -> int:
    if xp < 100: return 1
    if xp < 300: return 2
    if xp < 600: return 3
    if xp < 1000: return 4
    return 5

def send_reset_email(to_email: str, code: str):
    """Send password reset code via Gmail SMTP."""
    msg = MIMEText(
        f"你的 CyberLearn 密碼重設驗證碼是：\n\n{code}\n\n此驗證碼 10 分鐘內有效。\n如果不是你本人操作，請忽略此郵件。",
        "plain", "utf-8"
    )
    msg["Subject"] = "CyberLearn 密碼重設驗證碼"
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
        server.send_message(msg)


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    await init_db()

@app.post("/api/register")
async def register(req: RegisterRequest):
    nickname = req.nickname.strip()
    if len(nickname) < 2 or len(nickname) > 20:
        raise HTTPException(400, "暱稱長度需在 2–20 字元之間")
    if len(req.password) < 8:
        raise HTTPException(400, "密碼至少需要 8 個字元")

    pw_hash = ph.hash(req.password)
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("PRAGMA journal_mode=WAL")
            async with db.execute(
                "SELECT 1 FROM users WHERE nickname = ? COLLATE NOCASE",
                (nickname,)
            ) as cur:
                existed = await cur.fetchone()
            if existed:
                raise HTTPException(409, "這個暱稱已經被使用了，換一個試試？")
            await db.execute(
                "INSERT INTO users (nickname, password_hash) VALUES (?, ?)",
                (nickname, pw_hash)
            )
            await db.commit()
            async with db.execute("SELECT id FROM users WHERE nickname=?", (nickname,)) as cur:
                row = await cur.fetchone()
            return {"user_id": row[0], "nickname": nickname, "xp": 0, "level": 1}
    except aiosqlite.IntegrityError:
        raise HTTPException(409, "這個暱稱已經被使用了，換一個試試？")

@app.post("/api/login")
async def login(req: LoginRequest):
    nickname = req.nickname.strip()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        async with db.execute(
            "SELECT id, password_hash, xp, level, completed_lessons, email FROM users WHERE nickname=? COLLATE NOCASE",
            (nickname,)
        ) as cur:
            row = await cur.fetchone()
    if not row:
        raise HTTPException(401, "帳號或密碼錯誤")
    try:
        ph.verify(row[1], req.password)
    except VerifyMismatchError:
        raise HTTPException(401, "帳號或密碼錯誤")

    completed = json.loads(row[4] or "[]")
    return {
        "user_id": row[0],
        "nickname": nickname,
        "xp": row[2],
        "level": row[3],
        "completed_lessons": completed,
        "email": row[5] or ""
    }

@app.post("/api/bind_email")
async def bind_email(req: BindEmailRequest):
    email = req.email.strip().lower()
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        raise HTTPException(400, "Email 格式不正確")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        async with db.execute("SELECT id FROM users WHERE id=?", (req.user_id,)) as cur:
            if not await cur.fetchone():
                raise HTTPException(404, "找不到使用者")
        await db.execute("UPDATE users SET email=? WHERE id=?", (email, req.user_id))
        await db.commit()
    return {"ok": True, "email": email}

@app.post("/api/forgot_password")
async def forgot_password(req: ForgotPasswordRequest):
    email = req.email.strip().lower()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        async with db.execute("SELECT id FROM users WHERE email=? COLLATE NOCASE", (email,)) as cur:
            row = await cur.fetchone()
        if not row:
            raise HTTPException(404, "此 Email 尚未綁定任何帳號")
        user_id = row[0]
        code = ''.join(random.choices(string.digits, k=6))
        await db.execute(
            "INSERT INTO password_resets (user_id, code) VALUES (?, ?)",
            (user_id, code)
        )
        await db.commit()
    try:
        send_reset_email(email, code)
    except Exception as e:
        raise HTTPException(500, f"郵件發送失敗：{str(e)}")
    return {"ok": True, "message": "驗證碼已寄出，請查收信箱"}

@app.post("/api/reset_password")
async def reset_password(req: ResetPasswordRequest):
    email = req.email.strip().lower()
    if len(req.new_password) < 8:
        raise HTTPException(400, "密碼至少需要 8 個字元")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        async with db.execute("SELECT id FROM users WHERE email=? COLLATE NOCASE", (email,)) as cur:
            row = await cur.fetchone()
        if not row:
            raise HTTPException(404, "此 Email 尚未綁定任何帳號")
        user_id = row[0]
        async with db.execute(
            "SELECT id, created_at FROM password_resets WHERE user_id=? AND code=? AND used=0 ORDER BY created_at DESC LIMIT 1",
            (user_id, req.code)
        ) as cur:
            reset_row = await cur.fetchone()
        if not reset_row:
            raise HTTPException(400, "驗證碼無效或已使用")
        # Check 10 min expiry
        created = datetime.fromisoformat(reset_row[1])
        now = datetime.utcnow()
        if (now - created).total_seconds() > 600:
            raise HTTPException(400, "驗證碼已過期，請重新申請")
        pw_hash = ph.hash(req.new_password)
        await db.execute("UPDATE users SET password_hash=? WHERE id=?", (pw_hash, user_id))
        await db.execute("UPDATE password_resets SET used=1 WHERE id=?", (reset_row[0],))
        await db.commit()
    return {"ok": True, "message": "密碼已重設成功，請用新密碼登入"}

@app.get("/api/me/{user_id}")
async def get_me(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        async with db.execute(
            "SELECT id, nickname, xp, level, completed_lessons, email FROM users WHERE id=?",
            (user_id,)
        ) as cur:
            row = await cur.fetchone()
    if not row:
        raise HTTPException(404, "找不到使用者")
    return {
        "user_id": row[0],
        "nickname": row[1],
        "xp": row[2],
        "level": row[3],
        "completed_lessons": json.loads(row[4] or "[]"),
        "email": row[5] or ""
    }

@app.get("/api/lessons")
async def get_lessons():
    return list(LESSONS.values())

@app.get("/api/questions/{lesson_id}")
async def get_questions(lesson_id: str, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        # Get mastery score
        async with db.execute(
            "SELECT mastery_score FROM user_knowledge WHERE user_id=? AND topic=?",
            (user_id, lesson_id)
        ) as cur:
            row = await cur.fetchone()
        mastery = row[0] if row else 0.0

        # Get recent question ids (avoid repeating last 5)
        async with db.execute(
            "SELECT question_id FROM answer_history WHERE user_id=? ORDER BY answered_at DESC LIMIT 5",
            (user_id,)
        ) as cur:
            recent_ids = [r[0] for r in await cur.fetchall()]

        # Select difficulty based on mastery
        if mastery < 0.5:
            difficulty = 1
        elif mastery < 0.8:
            difficulty = 2
        else:
            difficulty = 3

        # Fetch questions
        async with db.execute(
            "SELECT * FROM questions WHERE topic=? AND layer=1 ORDER BY difficulty ASC LIMIT 3",
            (lesson_id,)
        ) as cur:
            rows = await cur.fetchall()
            cols = [d[0] for d in cur.description]

    questions = []
    for row in rows:
        q = dict(zip(cols, row))
        q["options"] = json.loads(q["options"])
        q["tags"] = json.loads(q.get("tags", "[]"))
        questions.append(q)

    return {"questions": questions, "mastery": mastery}

@app.post("/api/answer")
async def submit_answer(req: AnswerRequest):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        # Get correct answer
        async with db.execute(
            "SELECT answer, explanation, topic FROM questions WHERE id=?",
            (req.question_id,)
        ) as cur:
            row = await cur.fetchone()
        if not row:
            raise HTTPException(404, "找不到這道題目")

        correct_answer, explanation, topic = row
        is_correct = req.answer.strip().upper() == correct_answer.strip().upper()

        # Record answer
        await db.execute(
            "INSERT INTO answer_history (user_id, question_id, is_correct, time_spent_seconds) VALUES (?, ?, ?, ?)",
            (req.user_id, req.question_id, int(is_correct), req.time_spent)
        )

        # Update mastery score
        async with db.execute(
            "SELECT mastery_score, attempt_count FROM user_knowledge WHERE user_id=? AND topic=?",
            (req.user_id, topic)
        ) as cur:
            km = await cur.fetchone()

        if km:
            score, attempts = km
            new_score = min(1.0, score + 0.1) if is_correct else max(0.0, score - 0.05)
            await db.execute(
                "UPDATE user_knowledge SET mastery_score=?, last_practiced=datetime('now'), attempt_count=? WHERE user_id=? AND topic=?",
                (new_score, attempts + 1, req.user_id, topic)
            )
        else:
            new_score = 0.1 if is_correct else 0.0
            await db.execute(
                "INSERT INTO user_knowledge (user_id, topic, mastery_score, last_practiced, attempt_count) VALUES (?, ?, ?, datetime('now'), 1)",
                (req.user_id, topic, new_score)
            )

        await db.commit()

    return {
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "explanation": explanation,
        "mastery": new_score,
    }

@app.post("/api/complete_lesson")
async def complete_lesson(data: dict):
    user_id = data.get("user_id")
    lesson_id = data.get("lesson_id")
    if not user_id or not lesson_id:
        raise HTTPException(400, "缺少必要欄位")

    lesson = LESSONS.get(lesson_id)
    if not lesson:
        raise HTTPException(404, "找不到這個關卡")

    xp_reward = lesson.get("xp", 100)
    badge = lesson.get("badge", "🏅 學習徽章")

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        async with db.execute("SELECT xp, completed_lessons FROM users WHERE id=?", (user_id,)) as cur:
            row = await cur.fetchone()
        if not row:
            raise HTTPException(404, "找不到使用者")

        current_xp, completed_json = row
        completed = json.loads(completed_json or "[]")

        if lesson_id not in completed:
            completed.append(lesson_id)
            new_xp = current_xp + xp_reward
            new_level = xp_to_level(new_xp)
            await db.execute(
                "UPDATE users SET xp=?, level=?, completed_lessons=? WHERE id=?",
                (new_xp, new_level, json.dumps(completed), user_id)
            )
            await db.commit()
            return {"xp": new_xp, "level": new_level, "badge": badge, "xp_gained": xp_reward, "completed_lessons": completed}
        else:
            async with db.execute("SELECT xp, level FROM users WHERE id=?", (user_id,)) as cur:
                r = await cur.fetchone()
            return {"xp": r[0], "level": r[1], "badge": badge, "xp_gained": 0, "completed_lessons": completed}

# ─── Serve frontend ───────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt(request: Request):
    base = str(request.base_url).rstrip("/")
    return "\n".join([
        "User-agent: *",
        "Allow: /",
        "",
        f"Sitemap: {base}/sitemap.xml",
    ])

@app.get("/sitemap.xml")
async def sitemap_xml(request: Request):
    base = str(request.base_url).rstrip("/")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{base}/</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{base}/llms.txt</loc>
    <lastmod>{now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>
</urlset>"""
    return Response(content=xml, media_type="application/xml")

@app.get("/llms.txt", response_class=PlainTextResponse)
async def llms_txt(request: Request):
    base = str(request.base_url).rstrip("/")
    return "\n".join([
        "# CyberLearn",
        "",
        "> AI 驅動的防禦型資安學習平台，提供關卡式互動學習與基礎資安觀念訓練。",
        "",
        "## URL",
        f"- {base}/",
        "",
        "## Summary",
        "- 內容涵蓋密碼強度、釣魚郵件、社交工程、公共 WiFi 與 2FA。",
        "- 使用者可透過互動練習、測驗與 AI 對話完成學習關卡。",
    ])

app.mount("/static", StaticFiles(directory="static"), name="static")

# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
