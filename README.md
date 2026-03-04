<div align="center">

# 🛡️ CyberLearn — 防禦型資安學習平台

### _從陷阱中學會真正的防禦_

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-cybersecurity.nex11.me-00d4aa?style=for-the-badge)](https://cybersecurity.nex11.me)
[![GitHub Pages](https://img.shields.io/badge/📄_GitHub_Pages-yh11011.github.io-blue?style=for-the-badge)](https://yh11011.github.io)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/github/license/yh11011/Cybersecurity-study_web?style=for-the-badge)](LICENSE)

<br/>

> **CyberLearn** 是一個以「情境陷阱」為核心的互動式資安教學平台。  
> 學習者會先掉入精心設計的資安陷阱（如假密碼強度計），  
> 再透過知識說明與題庫測驗，從親身經歷中深刻理解資安威脅並學會防禦技巧。

</div>

---

## ✨ 核心特色

| 特色 | 說明 |
|------|------|
| 🪤 **情境陷阱教學** | 先讓使用者「親身中招」，再從錯誤中學習，印象更深刻 |
| 📖 **情境式知識說明** | 每關附詳細知識解說，從陷阱中帶出重要概念 |
| 🎮 **遊戲化學習** | XP 經驗值、等級升級、徽章蒐集，激勵持續學習 |
| 🧪 **選擇題測驗** | 每關配備情境題，附詳細解析與提示 |
| 🔒 **密碼安全設計** | Argon2id 雜湊、最小化個資蒐集 |
| 🌙 **賽博龐克 UI** | Glassmorphism 風格、霓虹配色、掃描線動畫 |

> 💡 **AI 對話功能**將在未來版本加入，目前以題庫與說明為主。

---

## 🎓 學習關卡一覽

| # | 關卡 | Emoji | 主題 | 徽章 | 狀態 |
|---|------|-------|------|------|------|
| 1 | **密碼強度** | 🔐 | 密碼強度與字典攻擊 | 🛡️ 密碼衛士 | ✅ 已上線 |
| 2 | **釣魚郵件** | 🎣 | 釣魚郵件辨識 | 🔍 郵件偵探 | 🔒 Phase 2 |
| 3 | **社交工程** | 🎭 | 社交工程攻擊 | 🧠 心理防禦師 | 🔒 Phase 2 |
| 4 | **公共 WiFi** | 📡 | 公共 WiFi 風險與中間人攻擊 | 📡 網路衛士 | 🔒 Phase 2 |
| 5 | **雙因素驗證** | 🔑 | 2FA 的重要性與運作原理 | 🔑 雙重守門人 | 🔒 Phase 2 |

---

## 🏗️ 技術架構

```
┌──────────────────────────────────────────────────────┐
│  Browser (SPA)                                       │
│  Alpine.js + TailwindCSS + Glassmorphism UI          │
├──────────────────────────────────────────────────────┤
│  Nginx (Reverse Proxy + SSL)                         │
├──────────────────────────────────────────────────────┤
│  FastAPI (async Python 3.11+)                        │
│  ├── Auth (Argon2id)     ├── Quiz System             │
│  ├── Lesson Engine       ├── XP & Level System       │
│  └── Email Reset                                     │
├──────────────────────────────────────────────────────┤
│  SQLite (WAL mode)                                   │
└──────────────────────────────────────────────────────┘
```

| 層 | 技術 | 說明 |
|----|------|------|
| **前端** | [Alpine.js](https://alpinejs.dev) + [TailwindCSS](https://tailwindcss.com) | CDN 引入，零 build 步驟 |
| **後端** | [FastAPI](https://fastapi.tiangolo.com) (Python 3.11+) | async 原生，高效能 |
| **資料庫** | [SQLite](https://sqlite.org) (WAL 模式) | 輕量高效，未來可升 PostgreSQL |
| **反代** | [Nginx](https://nginx.org) + [Let's Encrypt](https://letsencrypt.org) | HTTPS 加密 |
| **密碼** | [Argon2id](https://github.com/P-H-C/phc-winner-argon2) | OWASP 推薦的現代雜湊演算法 |
| **容器** | [Docker](https://docker.com) + Docker Compose | 一鍵部署，環境一致 |

---

## 📁 專案結構

```
Cybersecurity-study_web/
├── main.py                  # FastAPI 後端（API + DB + SEO）
├── index.html               # 前端 SPA 主模板（Alpine.js + Tailwind）
├── static/
│   └── index.html           # 實際部署版本（含 SEO meta tags）
├── docker-compose.yml       # Docker Compose 設定
├── Dockerfile               # Docker 映像檔定義
├── deploy.sh                # 一鍵部署腳本（Nginx + systemd）
├── deploy_docker.sh         # Docker 部署腳本
├── nginx.conf               # Nginx 反向代理設定
├── requirements.txt         # Python 依賴套件
├── docs/                    # 額外文件
└── README.md                # 本文件
```

---

## 🚀 快速開始

### 方式一：Docker 部署（推薦）

```bash
# 1. 克隆專案
git clone https://github.com/yh11011/Cybersecurity-study_web.git
cd Cybersecurity-study_web

# 2. 一鍵啟動
chmod +x deploy_docker.sh
./deploy_docker.sh
```

### 方式二：手動部署

```bash
# 1. 安裝依賴
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 啟動後端
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 方式三：生產環境部署（Nginx + SSL）

```bash
# 1. 執行一鍵部署腳本
chmod +x deploy.sh
sudo ./deploy.sh yourdomain.com

# 2. 或手動設定 Nginx
sudo cp nginx.conf /etc/nginx/sites-available/cyberlearn
sudo ln -sf /etc/nginx/sites-available/cyberlearn /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 3. SSL 憑證
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## ⚙️ 環境變數設定

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `CORS_ORIGINS` | `https://cybersecurity.nex11.me,...` | 允許的 CORS 來源 |
| `SMTP_EMAIL` | — | 忘記密碼功能的寄信信箱 |
| `SMTP_APP_PASSWORD` | — | Gmail App Password |

---

## 📊 API 端點

### 認證系統

| 方法 | 路徑 | 說明 |
|------|------|------|
| `POST` | `/api/register` | 使用者註冊（暱稱 + 密碼） |
| `POST` | `/api/login` | 使用者登入 |
| `POST` | `/api/bind_email` | 綁定 Email（用於密碼重設） |
| `POST` | `/api/forgot_password` | 忘記密碼（寄送驗證碼） |
| `POST` | `/api/reset_password` | 重設密碼 |

### 學習系統

| 方法 | 路徑 | 說明 |
|------|------|------|
| `GET` | `/api/lessons` | 取得所有關卡資料 |
| `GET` | `/api/questions/{lesson_id}` | 取得指定關卡的測驗題目 |
| `POST` | `/api/answer` | 提交答案 + 更新掌握分數 |
| `POST` | `/api/complete_lesson` | 完成關卡 + 發放 XP |

### SEO & 爬蟲

| 方法 | 路徑 | 說明 |
|------|------|------|
| `GET` | `/` | 首頁（SPA，含結構化資料） |
| `GET` | `/robots.txt` | 爬蟲規則與 Sitemap 入口 |
| `GET` | `/sitemap.xml` | XML Sitemap |
| `GET` | `/llms.txt` | 網站摘要 |

---

## 🛡️ 安全設計

### 密碼安全
- **Argon2id** 雜湊（OWASP 推薦，不儲存明文）
- 僅需暱稱即可註冊，最小化個人資訊蒐集
- 可選綁定 Email 支援密碼重設

### Nginx 限流
- `limit_req_zone` 全域限流防止濫用

---

## 🎓 功能清單 & 開發路線圖

### ✅ Phase 1 — MVP（已完成）

- [x] 使用者帳號系統（註冊 / 登入 / 忘記密碼）
- [x] 學習地圖（5 關，逐步解鎖機制）
- [x] 情境陷阱（關卡 1：假密碼強度計）
- [x] 情境知識說明（陷阱揭曉後的學習重點）
- [x] 選擇題測驗系統（含解析與提示）
- [x] 掌握分數計算（`user_knowledge` 表）
- [x] XP 經驗值與等級系統
- [x] Nginx 反向代理 + SSL
- [x] Docker 容器化部署
- [x] SEO 優化（Sitemap、robots.txt、JSON-LD、llms.txt）
- [x] 賽博龐克風格 UI（Glassmorphism + 霓虹配色）

### 🔜 Phase 2 — 內容擴充

- [ ] 全部 5 關內容與陷阱實作
- [ ] 遺忘曲線（48 小時後掌握分數衰減）
- [ ] 等級視覺化學習地圖
- [ ] 釣魚郵件陷阱（仿 Gmail UI）
- [ ] 假瀏覽器通知彈窗（HTML/CSS 模擬）

### 🔮 Phase 3 — AI 驅動（規劃中）

- [ ] AI 對話導師功能（SSE 串流）
- [ ] AI 驅動選題（知識狀態 JSON）
- [ ] AI 自動生成題目 + 人工審核
- [ ] Prompt Injection 防護
- [ ] 升級 PostgreSQL 資料庫

---

## 📝 常見問題

<details>
<summary><b>Q: database locked 錯誤？</b></summary>

確認 SQLite 的 `PRAGMA journal_mode=WAL` 有設定。WAL 模式支援多個讀取者同時讀取，大幅減少鎖定問題。本專案已在初始化時自動設定。
</details>

<details>
<summary><b>Q: 如何查看日誌？</b></summary>

```bash
# Docker 部署
docker logs -f cyberlearn-web

# systemd 部署
journalctl -u cyberlearn -f
```
</details>

---

## 🔗 相關連結

| 連結 | 說明 |
|------|------|
| 🌐 [cybersecurity.nex11.me](https://cybersecurity.nex11.me) | 線上 Demo（Live） |
| 📄 [GitHub Pages](https://yh11011.github.io) | 靜態前端頁面 |
| 📦 [GitHub Repo](https://github.com/yh11011/Cybersecurity-study_web) | 原始碼 |
| ⚡ [FastAPI Docs](https://fastapi.tiangolo.com) | 後端框架文件 |
| 🎨 [Alpine.js](https://alpinejs.dev) | 前端互動框架 |
| 🖌️ [TailwindCSS](https://tailwindcss.com) | 前端 CSS 框架 |

---

<div align="center">

**Made with 🛡️ by [yh11011](https://github.com/yh11011)**

_用知識守護每一位網路使用者的安全意識_

</div>
