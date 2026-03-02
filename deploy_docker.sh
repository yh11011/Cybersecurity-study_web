#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"
PORT="${1:-8000}"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker 未安裝，請先安裝 Docker。"
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "找不到 docker compose，請先安裝 Docker Compose。"
  exit 1
fi

APP_PORT="$PORT" "${COMPOSE_CMD[@]}" up -d --build

SERVER_IP="${SERVER_IP:-$(hostname -I | awk '{print $1}')}"
echo "部署完成。"
echo "網站連結: http://${SERVER_IP}:${PORT}"
echo "若在本機測試，也可用: http://localhost:${PORT}"
