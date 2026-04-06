"""
AB Logistic Telegram Bot â ÐÑÐ¸ÑÐ¼ Ð·Ð°ÑÐ²Ð¾Ðº Ñ ÑÐ°Ð¹ÑÐ° + TG-Ð¸Ð½ÑÐµÑÑÐµÐ¹Ñ
ÐÐ¾Ñ: @ab_cargo_bot
ÐÐµÑÑÐ¸Ñ: 1.0
"""

import asyncio
import logging
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from aiohttp import web
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import (
    BOT_TOKEN, MANAGER_GROUP_ID, WEBHOOK_PORT, WEBHOOK_SECRET,
    EMAIL_FROM, EMAIL_TO, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
)

# ============ LOGGING ============
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ============ BOT INIT ============
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# ============ COUNTER ============
lead_counter = {"count": 0}

# ============ KEYBOARDS ============
def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ÐÑÑÐ°Ð²Ð¸ÑÑ Ð·Ð°ÑÐ²ÐºÑ", callback_data="leave_request")],
        [InlineKeyboardButton(text="Ð ÐºÐ¾Ð¼Ð¿Ð°Ð½Ð¸Ð¸", callback_data="about")],
        [InlineKeyboardButton(text="Ð¡Ð²ÑÐ·Ð°ÑÑÑÑ Ñ Ð¼ÐµÐ½ÐµÐ´Ð¶ÐµÑÐ¾Ð¼", callback_data="contact")],
    ])

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ÐÑÑÐ°Ð²Ð¸ÑÑ Ð·Ð°ÑÐ²ÐºÑ", callback_data="leave_request")],
        [InlineKeyboardButton(text="Ð Ð¼ÐµÐ½Ñ", callback_data="main_menu")],
    ])

def after_lead_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ÐÐ¾Ð´Ð¿Ð¸ÑÐ°ÑÑÑÑ Ð½Ð° ÐºÐ°Ð½Ð°Ð»", url="https://t.me/ablogistic")],
        [InlineKeyboardButton(text="Ð Ð¼ÐµÐ½Ñ", callback_data="main_menu")],
    ])


# ============ FSM: Ð·Ð°ÑÐ²ÐºÐ° ÑÐµÑÐµÐ· Ð±Ð¾ÑÐ° ============
class LeadForm(StatesGroup):
    name = State()
    phone = State()
    message = State()


# ============ HELPERS ============
def format_site_lead(data: dict, lead_id: int) -> str:
    """Ð¤Ð¾ÑÐ¼Ð°ÑÐ¸ÑÐ¾Ð²Ð°Ð½Ð¸Ðµ Ð·Ð°ÑÐ²ÐºÐ¸ Ñ Ð¡ÐÐÐ¢Ð."""
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    lines = [
        f"ÐÐÐÐÐ¯ ÐÐÐ¯ÐÐÐ #{lead_id:04d}",
        "âââââââââââââââââ",
    ]
    if data.get("name"):
        lines.append(f"ÐÐ¼Ñ: {data['name']}")
    if data.get("phone"):
        lines.append(f"Ð¢ÐµÐ»: {data['phone']}")
    if data.get("email"):
        lines.append(f"Email: {data['email']}")
    if data.get("company"):
        lines.append(f"ÐÐ¾Ð¼Ð¿Ð°Ð½Ð¸Ñ: {data['company']}")
    if data.get("message"):
        lines.append(f"Ð¡Ð¾Ð¾Ð±ÑÐµÐ½Ð¸Ðµ: {data['message']}")
    if data.get("cargo"):
        lines.append(f"ÐÑÑÐ·: {data['cargo']}")
    if data.get("origin"):
        lines.append(f"ÐÑÐºÑÐ´Ð°: {data['origin']}")
    if data.get("destination"):
        lines.append(f"ÐÑÐ´Ð°: {data['destination']}")
    if data.get("volume"):
        lines.append(f"ÐÐ±ÑÑÐ¼: {data['volume']}")
    lines.append("âââââââââââââââââ")
    lines.append(f"ÐÐ°ÑÐ°: {now}")
    lines.append(f"ÐÑÑÐ¾ÑÐ½Ð¸Ðº: {data.get('source', 'Ð¡Ð°Ð¹Ñ vedlink.ru')}")
    return "\n".join(lines)


def format_bot_lead(data: dict, lead_id: int) -> str:
    """Ð¤Ð¾ÑÐ¼Ð°ÑÐ¸ÑÐ¾Ð²Ð°Ð½Ð¸Ðµ Ð·Ð°ÑÐ²ÐºÐ¸ Ð¸Ð· ÐÐÐ¢Ð."""
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    return (
        f"ÐÐÐÐÐ¯ ÐÐÐ¯ÐÐÐ #{lead_id:04d}\n"
        f"âââââââââââââââââ\n"
        f"ÐÐ¼Ñ: {data['name']}\n"
        f"Ð¢ÐµÐ»: {data['phone']}\n"
        f"Ð¡Ð¾Ð¾Ð±ÑÐµÐ½Ð¸Ðµ: {data.get('message', 'â')}\n"
        f"TG: {data.get('tg_username', 'Ð½Ðµ ÑÐºÐ°Ð·Ð°Ð½')}\n"
        f"âââââââââââââââââ\n"
        f"ÐÐ°ÑÐ°: {now}\n"
        f"ÐÑÑÐ¾ÑÐ½Ð¸Ðº: Telegram-Ð±Ð¾Ñ"
    )


async def send_to_group(text: str):
    """ÐÑÐ¿ÑÐ°Ð²ÐºÐ° Ð² TG-Ð³ÑÑÐ¿Ð¿Ñ Ð¼ÐµÐ½ÐµÐ´Ð¶ÐµÑÐ¾Ð²."""
    try:
        await bot.send_message(chat_id=MANAGER_GROUP_ID, text=text)
        logger.info("ÐÐ°ÑÐ²ÐºÐ° Ð¾ÑÐ¿ÑÐ°Ð²Ð»ÐµÐ½Ð° Ð² Ð³ÑÑÐ¿Ð¿Ñ Ð¼ÐµÐ½ÐµÐ´Ð¶ÐµÑÐ¾Ð²")
    except Exception as e:
        logger.error(f"ÐÑÐ¸Ð±ÐºÐ° Ð¾ÑÐ¿ÑÐ°Ð²ÐºÐ¸ Ð² Ð³ÑÑÐ¿Ð¿Ñ: {e}")


async def send_email(lead_text: str, lead_id: int):
    """ÐÑÐ¿ÑÐ°Ð²ÐºÐ° Ð½Ð° email ÑÐµÑÐµÐ· SMTP."""
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        msg["Subject"] = f"ÐÐ¾Ð²Ð°Ñ Ð·Ð°ÑÐ²ÐºÐ° #{lead_id:04d} â AB Logistic"
        body = lead_text.replace("â", "-")
        msg.attach(MIMEText(body, "plain", "utf-8"))

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _send_smtp, msg)
        logger.info(f"Email Ð¾ÑÐ¿ÑÐ°Ð²Ð»ÐµÐ½ Ð´Ð»Ñ Ð·Ð°ÑÐ²ÐºÐ¸ #{lead_id:04d}")
    except Exception as e:
        logger.error(f"ÐÑÐ¸Ð±ÐºÐ° Ð¾ÑÐ¿ÑÐ°Ð²ÐºÐ¸ email: {e}")


def _send_smtp(msg):
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)


def next_lead_id():
    lead_counter["count"] += 1
    return lead_counter["count"]


# ================================================================
#  Ð§ÐÐ¡Ð¢Ð¬ 1: WEBHOOK â Ð¿ÑÐ¸ÑÐ¼ Ð·Ð°ÑÐ²Ð¾Ðº Ñ ÑÐ°Ð¹ÑÐ°
# ================================================================

async def handle_webhook(request: web.Request):
    """
    ÐÑÐ¸Ð½Ð¸Ð¼Ð°ÐµÑ POST-Ð·Ð°Ð¿ÑÐ¾Ñ Ñ ÑÐ¾ÑÐ¼Ñ ÑÐ°Ð¹ÑÐ°.
    ÐÐ¾Ð´Ð´ÐµÑÐ¶Ð¸Ð²Ð°ÐµÐ¼ÑÐµ Ð¿Ð¾Ð»Ñ: name, phone, email, company, message,
                         cargo, origin, destination, volume, source
    """
    # ÐÐ¾Ð»ÑÑÐ°ÐµÐ¼ Ð´Ð°Ð½Ð½ÑÐµ
    try:
        data = await request.json()
    except Exception:
        data = dict(await request.post())

    # ÐÑÐ¾Ð²ÐµÑÑÐµÐ¼ ÑÐµÐºÑÐµÑÐ½ÑÐ¹ ÐºÐ»ÑÑ (Ð·Ð°ÑÐ¸ÑÐ° Ð¾Ñ ÑÐ¿Ð°Ð¼Ð°)
    if WEBHOOK_SECRET:
        secret = request.headers.get("X-Webhook-Secret", "") or data.get("secret", "")
        if secret != WEBHOOK_SECRET:
            logger.warning("ÐÐµÐ²ÐµÑÐ½ÑÐ¹ ÑÐµÐºÑÐµÑ webhook")
            return web.json_response({"error": "forbidden"}, status=403)

    logger.info(f"ÐÐ¾Ð»ÑÑÐµÐ½Ð° Ð·Ð°ÑÐ²ÐºÐ° Ñ ÑÐ°Ð¹ÑÐ°: {data}")

    # Ð£Ð±Ð¸ÑÐ°ÐµÐ¼ ÑÐµÐºÑÐµÑ Ð¸Ð· Ð´Ð°Ð½Ð½ÑÑ
    data.pop("secret", None)

    # ÐÐµÐ½ÐµÑÐ¸ÑÑÐµÐ¼ ID
    lead_id = next_lead_id()

    # Ð¤Ð¾ÑÐ¼Ð°ÑÐ¸ÑÑÐµÐ¼
    lead_text = format_site_lead(data, lead_id)

    # ÐÑÐ¿ÑÐ°Ð²Ð»ÑÐµÐ¼ Ð² Ð³ÑÑÐ¿Ð¿Ñ + email Ð¿Ð°ÑÐ°Ð»Ð»ÐµÐ»ÑÐ½Ð¾
    await asyncio.gather(
        send_to_group(lead_text),
        send_email(lead_text, lead_id)
    )

    return web.json_response({
        "ok": True,
        "lead_id": lead_id,
        "message": "ÐÐ°ÑÐ²ÐºÐ° Ð¿ÑÐ¸Ð½ÑÑÐ°"
    })


async def handle_options(request: web.Request):
    """CORS preflight Ð´Ð»Ñ fetch Ñ ÑÐ°Ð¹ÑÐ°."""
    return web.Response(
        status=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, X-Webhook-Secret",
        }
    )


# ================================================================
#  Ð§ÐÐ¡Ð¢Ð¬ 2: TELEGRAM-ÐÐÐ¢ â Ð¸Ð½ÑÐµÑÑÐµÐ¹Ñ Ð² Telegram
# ================================================================

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    text = (
        "<b>ÐÐ´ÑÐ°Ð²ÑÑÐ²ÑÐ¹ÑÐµ! Ð­ÑÐ¾ AB Logistic</b> â ÑÐ°Ð¼Ð¾Ð¶ÐµÐ½Ð½ÑÐ¹ Ð¿ÑÐµÐ´ÑÑÐ°Ð²Ð¸ÑÐµÐ»Ñ "
        "Ð¸ Ð»Ð¾Ð³Ð¸ÑÑÐ¸ÑÐµÑÐºÐ¸Ð¹ Ð¾Ð¿ÐµÑÐ°ÑÐ¾Ñ.\n\n"
        "ÐÐ¾ÑÑÐ°Ð²Ð»ÑÐµÐ¼ Ð³ÑÑÐ·Ñ Ð¸Ð· ÐÐ¸ÑÐ°Ñ, Ð®Ð¶Ð½Ð¾Ð¹ ÐÐ¾ÑÐµÐ¸, Ð¢ÑÑÑÐ¸Ð¸ Ð¸ ÐÐ²ÑÐ¾Ð¿Ñ "
        "Ð² Ð Ð¾ÑÑÐ¸Ñ. ÐÐ¾Ð»Ð½ÑÐ¹ ÑÐ¸ÐºÐ»: Ð¾Ñ Ð·Ð°ÐºÑÐ¿ÐºÐ¸ Ð´Ð¾ Ð´Ð¾ÑÑÐ°Ð²ÐºÐ¸ Ð´Ð¾ Ð´Ð²ÐµÑÐ¸.\n\n"
        "<i>ÐÐ¸ÑÐµÐ½Ð·Ð¸Ñ Ð¢Ð â1776 | Ð Ð°Ð±Ð¾ÑÐ°ÐµÐ¼ Ð¿Ð¾ Ð²ÑÐµÐ¹ Ð Ð¾ÑÑÐ¸Ð¸</i>\n\n"
        "ÐÑÐ±ÐµÑÐ¸ÑÐµ Ð´ÐµÐ¹ÑÑÐ²Ð¸Ðµ:"
    )
    await message.answer(text, reply_markup=main_menu_kb(), parse_mode="HTML")


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "<b>AB Logistic</b> â ÑÐ°Ð¼Ð¾Ð¶ÐµÐ½Ð½ÑÐ¹ Ð¿ÑÐµÐ´ÑÑÐ°Ð²Ð¸ÑÐµÐ»Ñ "
        "Ð¸ Ð»Ð¾Ð³Ð¸ÑÑÐ¸ÑÐµÑÐºÐ¸Ð¹ Ð¾Ð¿ÐµÑÐ°ÑÐ¾Ñ.\n\n"
        "ÐÑÐ±ÐµÑÐ¸ÑÐµ Ð´ÐµÐ¹ÑÑÐ²Ð¸Ðµ:"
    )
    await callback.message.edit_text(text, reply_markup=main_menu_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "about")
async def cb_about(callback: CallbackQuery):
    text = (
        "<b>AB Logistic (ÐÐÐ Â«Ð­Ð ÐÐ ÐÐÐÐÐ¡Ð¢ÐÐÂ»)</b>\n\n"
        "Ð¢Ð°Ð¼Ð¾Ð¶ÐµÐ½Ð½ÑÐ¹ Ð¿ÑÐµÐ´ÑÑÐ°Ð²Ð¸ÑÐµÐ»Ñ. ÐÐ¸ÑÐµÐ½Ð·Ð¸Ñ Ð¢Ð â1776\n"
        "Ð¡Ð²Ð¸Ð´ÐµÑÐµÐ»ÑÑÑÐ²Ð¾ â05-40/30828\n\n"
        "<b>Ð£ÑÐ»ÑÐ³Ð¸:</b>\n"
        "â ÐÐ¾ÑÑÐ°Ð²ÐºÐ° Ð¸Ð· ÐÐ¸ÑÐ°Ñ, Ð®. ÐÐ¾ÑÐµÐ¸, Ð¢ÑÑÑÐ¸Ð¸, ÐÐ²ÑÐ¾Ð¿Ñ\n"
        "â Ð¢Ð°Ð¼Ð¾Ð¶ÐµÐ½Ð½Ð¾Ðµ Ð¾ÑÐ¾ÑÐ¼Ð»ÐµÐ½Ð¸Ðµ (Ð´Ð¾ 12 ÑÐ°ÑÐ¾Ð²)\n"
        "â Ð¡Ð±Ð¾ÑÐ½ÑÐµ Ð³ÑÑÐ·Ñ (ÐºÐ¾Ð½ÑÐ¾Ð»Ð¸Ð´Ð°ÑÐ¸Ñ Ð² ÐÐ¸ÑÐ°Ðµ)\n"
        "â ÐÐ³ÐµÐ½ÑÑÐºÐ¸Ðµ Ð¿Ð»Ð°ÑÐµÐ¶Ð¸ (EUR, USD)\n"
        "â Ð¡ÐµÑÑÐ¸ÑÐ¸ÐºÐ°ÑÐ¸Ñ Ð¸ Ð§ÐµÑÑÐ½ÑÐ¹ Ð·Ð½Ð°Ðº\n"
        "â Ð¡ÑÑÐ°ÑÐ¾Ð²Ð°Ð½Ð¸Ðµ Ð³ÑÑÐ·Ð¾Ð²\n\n"
        "<b>ÐÑÐ¸ÑÑ:</b> Ð Ð¾ÑÑÐ¸Ñ, ÐÐ¸ÑÐ°Ð¹, Ð®Ð¶Ð½Ð°Ñ ÐÐ¾ÑÐµÑ\n"
        "<b>Ð¡Ð°Ð¹Ñ:</b> vedlink.ru\n"
        "<b>Ð¢ÐµÐ»:</b> +7 (812) 920-28-44"
    )
    await callback.message.edit_text(text, reply_markup=back_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "contact")
async def cb_contact(callback: CallbackQuery):
    text = (
        "<b>Ð¡Ð²ÑÐ¶Ð¸ÑÐµÑÑ Ñ Ð½Ð°Ð¼Ð¸:</b>\n\n"
        "Ð¢ÐµÐ»ÐµÑÐ¾Ð½: +7 (812) 920-28-44\n"
        "Email: greenray@ablogistic.pro\n"
        "WhatsApp: +7 (925) 005-51-44\n\n"
        "ÐÐ»Ð¸ Ð¾ÑÑÐ°Ð²ÑÑÐµ Ð·Ð°ÑÐ²ÐºÑ â Ð¼ÐµÐ½ÐµÐ´Ð¶ÐµÑ ÑÐ²ÑÐ¶ÐµÑÑÑ "
        "Ð² ÑÐµÑÐµÐ½Ð¸Ðµ 30 Ð¼Ð¸Ð½ÑÑ (9:00-18:00 ÐÐ¡Ð)."
    )
    await callback.message.edit_text(text, reply_markup=back_kb(), parse_mode="HTML")
    await callback.answer()


# --- ÐÐ°ÑÐ²ÐºÐ° ÑÐµÑÐµÐ· Ð±Ð¾ÑÐ° ---
@router.callback_query(F.data == "leave_request")
async def cb_leave_request(callback: CallbackQuery, state: FSMContext):
    tg_username = "Ð½Ðµ ÑÐºÐ°Ð·Ð°Ð½"
    if callback.from_user and callback.from_user.username:
        tg_username = f"@{callback.from_user.username}"
    await state.update_data(tg_username=tg_username)
    await state.set_state(LeadForm.name)

    text = "<b>ÐÐ°Ðº Ð²Ð°Ñ Ð·Ð¾Ð²ÑÑ?</b>\n<i>Ð£ÐºÐ°Ð¶Ð¸ÑÐµ Ð¸Ð¼Ñ Ð¸ ÐºÐ¾Ð¼Ð¿Ð°Ð½Ð¸Ñ (ÐµÑÐ»Ð¸ ÐµÑÑÑ)</i>"
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()


@router.message(LeadForm.name)
async def msg_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Ð£ÐºÐ°Ð¶Ð¸ÑÐµ Ð¸Ð¼Ñ (Ð¼Ð¸Ð½Ð¸Ð¼ÑÐ¼ 2 ÑÐ¸Ð¼Ð²Ð¾Ð»Ð°).")
        return
    await state.update_data(name=name)
    await state.set_state(LeadForm.phone)
    await message.answer("<b>Ð¢ÐµÐ»ÐµÑÐ¾Ð½ Ð´Ð»Ñ ÑÐ²ÑÐ·Ð¸:</b>", parse_mode="HTML")


@router.message(LeadForm.phone)
async def msg_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) < 7:
        await message.answer("Ð£ÐºÐ°Ð¶Ð¸ÑÐµ ÐºÐ¾ÑÑÐµÐºÑÐ½ÑÐ¹ Ð½Ð¾Ð¼ÐµÑ (Ð¼Ð¸Ð½Ð¸Ð¼ÑÐ¼ 7 ÑÐ¸ÑÑ).")
        return
    await state.update_data(phone=phone)
    await state.set_state(LeadForm.message)

    skip_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ÐÑÐ¾Ð¿ÑÑÑÐ¸ÑÑ", callback_data="skip_message")]
    ])
    await message.answer(
        "<b>ÐÐ¿Ð¸ÑÐ¸ÑÐµ ÑÑÐ¾ Ð½ÑÐ¶Ð½Ð¾ Ð´Ð¾ÑÑÐ°Ð²Ð¸ÑÑ</b>\n<i>(Ð¸Ð»Ð¸ Ð½Ð°Ð¶Ð¼Ð¸ÑÐµ ÐÑÐ¾Ð¿ÑÑÑÐ¸ÑÑ)</i>",
        reply_markup=skip_kb, parse_mode="HTML"
    )


@router.message(LeadForm.message)
async def msg_message(message: Message, state: FSMContext):
    await state.update_data(message=message.text.strip())
    await _finalize_bot_lead(message, state)


@router.callback_query(LeadForm.message, F.data == "skip_message")
async def cb_skip_message(callback: CallbackQuery, state: FSMContext):
    await state.update_data(message="â")
    await callback.answer()
    await _finalize_bot_lead(callback.message, state, from_callback=True)


async def _finalize_bot_lead(message: Message, state: FSMContext, from_callback=False):
    data = await state.get_data()
    await state.clear()

    lead_id = next_lead_id()
    lead_text = format_bot_lead(data, lead_id)

    await asyncio.gather(
        send_to_group(lead_text),
        send_email(lead_text, lead_id)
    )

    thanks = (
        f"<b>Ð¡Ð¿Ð°ÑÐ¸Ð±Ð¾! ÐÐ°ÑÐ²ÐºÐ° #{lead_id:04d} Ð¿ÑÐ¸Ð½ÑÑÐ°.</b>\n\n"
        "ÐÐµÐ½ÐµÐ´Ð¶ÐµÑ ÑÐ²ÑÐ¶ÐµÑÑÑ Ð² ÑÐµÑÐµÐ½Ð¸Ðµ 30 Ð¼Ð¸Ð½ÑÑ "
        "(9:00-18:00 ÐÐ¡Ð).\n\n"
        "ÐÐ¾Ð´Ð¿Ð¸ÑÑÐ²Ð°Ð¹ÑÐµÑÑ Ð½Ð° ÐºÐ°Ð½Ð°Ð» â Ð¿Ð¾Ð»ÐµÐ·Ð½ÑÐµ Ð¼Ð°ÑÐµÑÐ¸Ð°Ð»Ñ Ð¿Ð¾ ÐÐ­Ð."
    )

    if from_callback:
        await message.edit_text(thanks, reply_markup=after_lead_kb(), parse_mode="HTML")
    else:
        await message.answer(thanks, reply_markup=after_lead_kb(), parse_mode="HTML")


# ================================================================
#  ÐÐÐÐ£Ð¡Ð: Ð±Ð¾Ñ + Ð²ÐµÐ±-ÑÐµÑÐ²ÐµÑ Ð¾Ð´Ð½Ð¾Ð²ÑÐµÐ¼ÐµÐ½Ð½Ð¾
# ================================================================

async def main():
    # ÐÐµÐ±-ÑÐµÑÐ²ÐµÑ Ð´Ð»Ñ Ð¿ÑÐ¸ÑÐ¼Ð° webhook Ñ ÑÐ°Ð¹ÑÐ°
    app = web.Application()
    app.router.add_post("/webhook/lead", handle_webhook)
    app.router.add_options("/webhook/lead", handle_options)

    @web.middleware
    async def cors_middleware(request, handler):
        response = await handler(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    app.middlewares.append(cors_middleware)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", WEBHOOK_PORT)
    await site.start()
    logger.info(f"Webhook-ÑÐµÑÐ²ÐµÑ Ð·Ð°Ð¿ÑÑÐµÐ½ Ð½Ð° Ð¿Ð¾ÑÑÑ {WEBHOOK_PORT}")

    # Telegram-Ð±Ð¾Ñ
    logger.info("ÐÐ¾Ñ @ab_cargo_bot Ð·Ð°Ð¿ÑÑÐµÐ½")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
