"""
Конфигурация бота AB Logistic (@ab_cargo_bot)
"""

import os

# ============ TELEGRAM ============
BOT_TOKEN = os.getenv("BOT_TOKEN", "8756777724:AAF2BmK9eMr9l1U-kcaGC9eFB8MvN0hsWP4")
MANAGER_GROUP_ID = int(os.getenv("MANAGER_GROUP_ID", "-1003709177161"))

# ============ WEBHOOK (приём заявок с сайта) ============
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8080"))
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "ab_logistic_2026_secret")

# ============ EMAIL (Yandex 360) ============
EMAIL_FROM = os.getenv("EMAIL_FROM", "sales@vedlink.ru")
EMAIL_TO = os.getenv("EMAIL_TO", "sales@vedlink.ru")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.yandex.ru")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "sales@vedlink.ru")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "rszugivuwmmjuyaf")
