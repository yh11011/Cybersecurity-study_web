# CyberLearn — AI 驅動防禦型資安學習平台

> Phase 1 MVP — 關卡 1 完整流程

## 📁 專案結構

```
cyberlearn/
├── main.py           # FastAPI 後端（API + AI 串接 + DB）
├── static/
│   └── index.html    # 前端 SPA（Alpine.js + TailwindCSS）
├── requirements.txt  # Python 套件
├── nginx.conf        # Nginx 反向代理設定
├── deploy.sh         # 一鍵部署腳本
└── README.md         # 本文件
```

---

## 🚀 快速部署（Oracle Cloud ARM / Ubuntu 24.04）

### 前置條件

```bash
# 確認 Ollama 已安裝並下載 DeepSeek 模型
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull deepseek-r1:14b      # 主模型（~8GB，需要時間）
# ollama pull qwen:14b           # 備援模型（之後需要再拉）

# 確認 Ollama 服務在背景運行
ollama serve &
```

### 一鍵部署

```bash
git clone <your-repo>
cd cyberlearn

# 給 deploy.sh 執行權限
chmod +x deploy.sh

# 執行部署（替換為你的域名）
sudo ./deploy.sh yourdomain.com
```

### 手動部署

```bash
# 1. 安裝 Python 套件
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 啟動後端（開發模式）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 3. Nginx 設定（生產環境）
sudo cp nginx.conf /etc/nginx/sites-available/cyberlearn
sudo ln -sf /etc/nginx/sites-available/cyberlearn /etc/nginx/sites-enabled/
# 編輯 nginx.conf，將 YOUR_DOMAIN 替換為實際域名
sudo nginx -t && sudo systemctl reload nginx

# 4. SSL（生產環境）
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 🔧 設定

### 切換 AI 模型

在 `main.py` 第 17 行：

```python
OLLAMA_MODEL = "deepseek-r1:14b"  # 改為 "qwen:14b" 使用備援模型
```

### Rate Limit 調整

```python
RATE_LIMIT_PER_MIN = 10  # 每 session 每分鐘最多幾次 AI 呼叫
```

---

## 🏗️ 技術架構

| 層     | 技術                         | 說明                              |
|--------|------------------------------|-----------------------------------|
| 前端   | HTML + Alpine.js + Tailwind  | CDN 引入，零 build 步驟            |
| 後端   | Python FastAPI               | async 原生，SSE 串流支援           |
| 資料庫 | SQLite (WAL 模式)            | MVP 階段，Phase 3 可升 PostgreSQL |
| AI     | Ollama + DeepSeek 14B        | 本地推論，資料不離境               |
| 代理   | Nginx + Let's Encrypt        | HTTPS 必須，雙層 rate limit        |
| 密碼   | Argon2id                     | 現代最佳實踐                       |

---

## 📊 API 端點

| 方法 | 路徑                    | 說明                    |
|------|-------------------------|-------------------------|
| POST | `/api/register`         | 使用者註冊               |
| POST | `/api/login`            | 使用者登入               |
| GET  | `/api/lessons`          | 取得所有關卡             |
| POST | `/api/chat`             | AI 對話（SSE 串流）      |
| GET  | `/api/questions/{id}`   | 取得關卡題目             |
| POST | `/api/answer`           | 提交答案 + 更新掌握分數  |
| POST | `/api/complete_lesson`  | 完成關卡 + 發放 XP       |

---

## 🎓 Phase 1 功能清單

- [x] 使用者帳號（暱稱 + Argon2id 密碼雜湊）
- [x] 學習地圖（5 關，逐步解鎖）
- [x] 情境陷阱（關卡 1：假密碼強度計）
- [x] AI 對話（DeepSeek + SSE 串流）
- [x] Prompt Injection 防護
- [x] Rate Limit（API + Nginx 雙層）
- [x] 選擇題測驗系統
- [x] 掌握分數計算（user_knowledge 表）
- [x] XP 與等級系統
- [x] Nginx 反向代理設定

## 🔜 Phase 2 待辦

- [ ] 全部 5 關內容與陷阱實作
- [ ] 遺忘曲線（48 小時後掌握分數衰減）
- [ ] 等級視覺化學習地圖
- [ ] 釣魚郵件陷阱（仿 Gmail UI）
- [ ] 假瀏覽器通知彈窗（HTML/CSS 模擬）

## 🔜 Phase 3 待辦

- [ ] DeepSeek 驅動選題（知識狀態 JSON）
- [ ] AI 自動生成題目 + 人工審核
- [ ] 外部 AI 工具整合（第三層）

---

## 🛡️ 安全設計

### Prompt Injection 防護
- 關鍵字偵測（regex）+ 攔截記錄
- 輸入長度限制（500 字）
- 每 session 獨立，對話不持久化
- Layer 1 自動遮蔽程式碼區塊

### 密碼安全
- Argon2id 雜湊（不儲存明文）
- 只需暱稱，不需 email

### 速率限制
- FastAPI 層：每 session 每分鐘 10 次 AI 呼叫
- Nginx 層：`limit_req_zone` 雙層防護

---

## 📝 常見問題

**Q: AI 回應很慢怎麼辦？**  
A: CPU-only 模式下 14B 模型推論需要 15-60 秒，前端已有「阿安正在思考中⋯⋯」提示。可考慮使用更小的模型（如 7B）加速，或等待 GPU 資源。

**Q: `database locked` 錯誤？**  
A: 確認 `PRAGMA journal_mode=WAL` 有設定。WAL 模式支援多個讀取者同時讀，大幅減少鎖定問題。

**Q: 如何查看日誌？**  
```bash
journalctl -u cyberlearn -f          # 即時查看
journalctl -u cyberlearn --since today  # 今天的日誌
```

**Q: 如何更新程式碼？**  
```bash
cp main.py /opt/cyberlearn/
cp static/index.html /opt/cyberlearn/static/
systemctl restart cyberlearn
```
