"""Конфигурация бота AB Logistic (@ab_cargo_bot)"""
import os

# ============ TELEGRAM ============
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MANAGER_GROUP_ID = int(os.getenv("MANAGER_GROUP_ID", "0"))

# ============ WEBHOOK (приём заявок с сайта) ============
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8080"))
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

# ============ EMAIL (Yandex 360) ============
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.yandex.ru")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
