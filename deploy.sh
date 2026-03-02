#!/bin/bash
# ================================================================
# CyberLearn — Phase 1 MVP 部署腳本
# 適用於 Oracle Cloud ARM / Ubuntu 24.04
# 使用方式：chmod +x deploy.sh && sudo ./deploy.sh
# ================================================================

set -e  # 任何錯誤就停止
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

log() { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err() { echo -e "${RED}[✗]${NC} $1"; exit 1; }
step() { echo -e "\n${BLUE}━━ $1 ━━${NC}"; }

# ── 設定變數 ──────────────────────────────────────────────────────
DOMAIN="${1:-}"          # 第一個參數為域名，例如: ./deploy.sh cyberlearn.example.com
APP_DIR="/opt/cyberlearn"
APP_USER="cyberlearn"
PYTHON="python3"

# ── 前置檢查 ──────────────────────────────────────────────────────
step "前置檢查"
[[ $EUID -ne 0 ]] && err "請以 root 執行（sudo ./deploy.sh）"
[[ -z "$DOMAIN" ]] && err "請提供域名：./deploy.sh yourdomain.com"
log "域名: $DOMAIN"

# ── 系統套件 ──────────────────────────────────────────────────────
step "安裝系統套件"
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv nginx certbot python3-certbot-nginx curl
log "系統套件安裝完成"

# ── 建立應用程式使用者 ────────────────────────────────────────────
step "建立應用程式使用者"
if ! id "$APP_USER" &>/dev/null; then
    useradd --system --home-dir $APP_DIR --shell /bin/false $APP_USER
    log "建立使用者 $APP_USER"
else
    log "使用者 $APP_USER 已存在"
fi

# ── 複製應用程式檔案 ──────────────────────────────────────────────
step "複製應用程式檔案"
mkdir -p $APP_DIR/static
cp main.py $APP_DIR/
cp -r static/* $APP_DIR/static/
chown -R $APP_USER:$APP_USER $APP_DIR
log "檔案複製完成: $APP_DIR"

# ── Python 虛擬環境 ───────────────────────────────────────────────
step "建立 Python 虛擬環境"
cd $APP_DIR
sudo -u $APP_USER $PYTHON -m venv venv
sudo -u $APP_USER venv/bin/pip install -q --upgrade pip
sudo -u $APP_USER venv/bin/pip install -q \
    fastapi uvicorn[standard] \
    argon2-cffi aiosqlite \
    python-multipart httpx
log "Python 環境建立完成"

# ── Systemd service ───────────────────────────────────────────────
step "建立 Systemd 服務"
cat > /etc/systemd/system/cyberlearn.service <<EOF
[Unit]
Description=CyberLearn FastAPI Application
After=network.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 1
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=cyberlearn

# Security hardening
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=$APP_DIR

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cyberlearn
systemctl start cyberlearn
log "Systemd 服務啟動完成"

# ── Nginx ─────────────────────────────────────────────────────────
step "設定 Nginx"
sed "s/YOUR_DOMAIN/$DOMAIN/g" nginx.conf > /etc/nginx/sites-available/cyberlearn

# 先使用 HTTP-only 設定（SSL 申請前）
cat > /etc/nginx/sites-available/cyberlearn-temp <<EOF
server {
    listen 80;
    server_name $DOMAIN;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
    }
}
EOF

ln -sf /etc/nginx/sites-available/cyberlearn-temp /etc/nginx/sites-enabled/cyberlearn
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
log "Nginx 設定完成（暫用 HTTP）"

# ── Let's Encrypt SSL ─────────────────────────────────────────────
step "申請 SSL 憑證 (Let's Encrypt)"
warn "需要域名 $DOMAIN 已指向此伺服器 IP"
read -p "是否現在申請 SSL？(y/N): " APPLY_SSL

if [[ "$APPLY_SSL" =~ ^[Yy]$ ]]; then
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
    # 換成完整設定（含 SSL）
    ln -sf /etc/nginx/sites-available/cyberlearn /etc/nginx/sites-enabled/cyberlearn
    nginx -t && systemctl reload nginx
    log "SSL 憑證申請成功！"
else
    warn "跳過 SSL 申請，你可以之後手動執行：certbot --nginx -d $DOMAIN"
fi

# ── Ollama 檢查 ───────────────────────────────────────────────────
step "檢查 Ollama"
if command -v ollama &>/dev/null; then
    log "Ollama 已安裝"
    if ollama list 2>/dev/null | grep -q "deepseek"; then
        log "DeepSeek 模型已存在"
    else
        warn "未找到 DeepSeek 模型，嘗試下載..."
        warn "注意：在 CPU-only ARM 環境下，14B 模型需要 10-20 分鐘下載"
        ollama pull deepseek-r1:14b || warn "下載失敗，請手動執行: ollama pull deepseek-r1:14b"
    fi
else
    warn "Ollama 未安裝！請手動安裝："
    echo "  curl -fsSL https://ollama.ai/install.sh | sh"
    echo "  ollama pull deepseek-r1:14b"
fi

# ── 完成 ──────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🎉 CyberLearn Phase 1 部署完成！${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════${NC}"
echo ""
echo "  🌐 網站：http://$DOMAIN （或 https:// 如已申請 SSL）"
echo "  📊 服務狀態：systemctl status cyberlearn"
echo "  📋 查看日誌：journalctl -u cyberlearn -f"
echo "  🔄 重啟服務：systemctl restart cyberlearn"
echo ""
echo "  Ollama 指令："
echo "    ollama serve           # 啟動 Ollama"
echo "    ollama pull deepseek-r1:14b  # 下載主模型"
echo "    ollama pull qwen:14b   # 下載備援模型"
echo ""
