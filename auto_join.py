#!/usr/bin/env python3
import asyncio
import logging
import random
import os
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.errors import FloodWaitError

API_ID = 37608717
API_HASH = '89a0956ade52c8ec8cbe05ba31716a2e'
PHONE_NUMBER = '+14502599439'

CHATS_FILE = 'chats.txt'
PROCESSED_FILE = 'processed.txt'
LOG_FILE = 'auto_join.log'

MIN_INTERVAL = 30 * 60
MAX_INTERVAL = 3 * 60 * 60
MAX_JOINS_PER_DAY = 25

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

client = TelegramClient('auto_join_session', API_ID, API_HASH)

BUILTIN_CHATS = [
    '@ukrainians_in_us', '@ukrainian_us', 'NY State - Help Ukrainians',
    'УКРАЇНЦІ В НЬЮ-ЙОРК ТА США', '❤️Привет Украина❤️ЧАТ', 'Ukrainians in Toronto',
    'Ukraine to Canada', 'London Support Ukraine', 'Life Чат для общения украинцев',
    'Trafalgar Girls', 'UCNSW', 'REFUGEE HELPER', 'GRAN FORO UKR 24', 'Nomady',
    'SvitUA', 'Вільна Україна', 'Чат взаємодопомоги УВС', 'UART. Ukrainian ART journal',
    'Telegraf.Design', 'Deslove | Чат', 'META MUSEUM', 'Staff_shop', 'the Ukrainian Fashion',
    'Українці в Вашингтон О.К.', 'Українська Канада | Українці в Канаді', 'UA Canada- Ми в Канада',
    'Українці в Англії / Украинцы в Англии', 'UK for UA help | УКРАИНЦЫ в ВЕЛИКОБРИТАНИИ',
    'Українці в Британії', 'Украинцы в Лондоне/Українці у Лондоні', 'Англія UA',
    'УКРАЇНЦІ В НІМЕЧЧИНІ', '@DEUTSCHEUKRAINE', 'UKR_DE', 'germanyhelpsukraine',
    'Помощь украинцам в Германии', 'Українці в Італії', 'Українці в Неаполі',
    'Допомога Українцям в Італії', 'Українці в Іспанії', 'НАША ІСПАНІЯ',
    'Чат українців в Іспанії - Як вдома', 'Українці у Франції', 'польша | на связи | чат',
    'Ukrainian in Poland | Новини Польща', 'Чат для Українців у Катовіце та Польщі',
    'Украина | Польша | Варшава | Чат', 'Telegram-чат "Українці в Австралії | Чат Австралия"',
    'Ukrainians in Australia', 'Українці в Таїланді Бангкок', 'Українці в Ясах, Румунія',
    'Киев чат', 'Просто чат', 'ку', 'Graffiti Art', 'Graffiti World', 'UA Brand',
    'Дошка оголошень Гардероб UA', 'Trends shop in ua', 'uabariga', 'CasualIsland',
    'Товари без посередників', 'Український Бізнесмен', 'Бізнес і робота Україна',
    'Фрілансер UA', 'Український Freelance', 'crypto ukraine chat', 'Крипто чат Україна'
]

async def already_in_chat(chat_identifier):
    try:
        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                if dialog.entity.username and chat_identifier.lstrip('@') == dialog.entity.username:
                    return True
                if str(chat_identifier) == str(dialog.id):
                    return True
        return False
    except Exception as e:
        logger.warning(f"Ошибка проверки {chat_identifier}: {e}")
        return False

async def join_chat(chat_identifier):
    try:
        # Для публичных каналов и групп по username
        await client.join_channel(chat_identifier)
        logger.info(f"✅ Вступил: {chat_identifier}")
        return True
    except FloodWaitError as e:
        logger.warning(f"Flood wait {e.seconds} сек")
        await asyncio.sleep(e.seconds)
        return False
    except Exception as e:
        # Если не получилось join_channel, пробуем join_chat (для приватных ссылок-приглашений)
        try:
            await client.join_chat(chat_identifier)
            logger.info(f"✅ Вступил (по ссылке): {chat_identifier}")
            return True
        except Exception as e2:
            if 'already in chat' in str(e2).lower() or 'already a member' in str(e2).lower():
                logger.info(f"ℹ️ Уже в чате: {chat_identifier}")
                return True
            logger.error(f"❌ Ошибка {chat_identifier}: {e2}")
            return False

def load_chats():
    if os.path.exists(CHATS_FILE):
        with open(CHATS_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    else:
        return BUILTIN_CHATS

def load_processed():
    try:
        with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def save_processed(processed):
    with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
        for chat in processed:
            f.write(chat + '\n')

async def main():
    await client.start(phone=PHONE_NUMBER)
    logger.info("Клиент запущен")

    chats = load_chats()
    if not chats:
        logger.error("Нет чатов для обработки")
        return

    processed = load_processed()
    remaining = [c for c in chats if c not in processed]
    logger.info(f"Осталось вступить: {len(remaining)}")

    joins_today = 0
    last_reset = datetime.now().date()

    for chat in remaining:
        today = datetime.now().date()
        if today != last_reset:
            joins_today = 0
            last_reset = today

        if joins_today >= MAX_JOINS_PER_DAY:
            wait = (datetime.combine(today + timedelta(days=1), datetime.min.time()) - datetime.now()).total_seconds()
            logger.info(f"Лимит на сегодня. Ждём {wait/3600:.1f} ч")
            await asyncio.sleep(wait)
            joins_today = 0
            last_reset = datetime.now().date()

        if await already_in_chat(chat):
            processed.add(chat)
            save_processed(processed)
            continue

        success = await join_chat(chat)
        if success:
            processed.add(chat)
            save_processed(processed)
            joins_today += 1
        else:
            logger.warning(f"Пропускаем {chat}")

        if remaining.index(chat) < len(remaining)-1:
            delay = random.randint(MIN_INTERVAL, MAX_INTERVAL)
            logger.info(f"Пауза {delay//60} минут")
            await asyncio.sleep(delay)

    logger.info("Все чаты обработаны")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Остановлен")
