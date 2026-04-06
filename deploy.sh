#!/bin/bash
# ==============================================
# AB Logistic Bot — Deploy Script
# Запуск: bash deploy.sh
# ==============================================
set -e

APP_DIR="/opt/ablogistic-bot"
SERVICE_NAME="ablogistic-bot"

echo ">>> [1/6] Обновление системы..."
apt update -y && apt install -y python3 python3-pip python3-venv git ufw

echo ">>> [2/6] Копирование файлов..."
mkdir -p $APP_DIR
cp bot.py config.py requirements.txt $APP_DIR/

echo ">>> [3/6] Создание виртуального окружения..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ">>> [4/6] Создание systemd-сервиса..."
cat > /etc/systemd/system/${SERVICE_NAME}.service <<SVCEOF
[Unit]
Description=AB Logistic Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/venv/bin/python ${APP_DIR}/bot.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SVCEOF

echo ">>> [5/6] Запуск бота..."
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl restart ${SERVICE_NAME}

echo ">>> [6/6] Открытие порта 8080..."
ufw allow 8080/tcp 2>/dev/null || true
ufw allow 22/tcp 2>/dev/null || true

echo ""
echo "============================================"
echo "  BOT DEPLOYED SUCCESSFULLY!"
echo "============================================"
echo "  Статус:  systemctl status ${SERVICE_NAME}"
echo "  Логи:    journalctl -u ${SERVICE_NAME} -f"
echo "  Webhook: http://\$(hostname -I | awk '{print \$1}'):8080/webhook/lead"
echo "============================================"
