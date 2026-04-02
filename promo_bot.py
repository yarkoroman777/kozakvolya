#!/usr/bin/env python3
import asyncio
import logging
import random
from telethon import TelegramClient, events

API_ID = 37608717
API_HASH = '89a0956ade52c8ec8cbe05ba31716a2e'
PHONE_NUMBER = '+14502599439'
MY_TELEGRAM_ID = 8614044372
REDBUBBLE_URL = 'https://bit.ly/4daFLfm'

KEYWORDS = {
    'uk': ['футболка', 'мерч', 'одяг', 'вишиванка', 'козак', 'донат', 'допомога', 'волонтер', 'зсу', 'армія', 'дрони', 'гуманітарка', 'купити', 'підтримка', 'мистецтво', 'арт', 'графіті', 'малюнок', 'художник', 'дизайн', 'творчість', 'принт', 'патріотичний', 'сувенір', 'благодійність', 'збір', 'допоможи'],
    'ru': ['футболка', 'мерч', 'казак', 'донат', 'помощь', 'волонтёр', 'всу', 'армия', 'дроны', 'гуманитарка', 'купить', 'поддержка', 'искусство', 'арт', 'граффити', 'рисунок', 'художник', 'дизайн', 'творчество', 'принт', 'патриотический', 'сувенир', 'благотворительность', 'сбор', 'помоги'],
    'en': ['t-shirt', 'tshirt', 'shirt', 'merch', 'cossack', 'donate', 'donation', 'help', 'volunteer', 'ukraine', 'ukrainian', 'drone', 'humanitarian', 'buy', 'support', 'freedom', 'art', 'graffiti', 'drawing', 'design', 'artist', 'creativity', 'painting', 'print', 'patriotic', 'souvenir', 'charity', 'fundraiser']
}

ANSWERS = {
    'uk': [
        "Є футболка з козаком. 20% з продажу йде на дрони та гуманітарку. Посилання: {url}",
        "Ті, хто шукає патріотичний мерч – ось футболка з українським козаком. Частина виручки на допомогу. {url}",
        "Підтримай Україну – купи футболку з козаком! 20% на дрони та гуманітарку. {url}",
        "Унікальний дизайн футболки з козаком. Кожна покупка наближає перемогу. Деталі: {url}",
        "Футболка, яка об'єднує. 20% від вартості йде нашим захисникам. Замовити: {url}",
        "Патріотичний одяг зі сенсом. Донат на дрони з кожною футболкою. Посилання: {url}",
        "Стань частиною змін – обери футболку з козаком. 20% на допомогу армії. {url}",
        "Вдягни патріотизм. Кожна футболка – це внесок у перемогу. Замовити тут: {url}",
        "Унікальна футболка з козаком – подарунок для себе чи друга. 20% на ЗСУ. {url}",
        "Долучайся до допомоги – купуй футболку з українським козаком. {url}",
        "Мерч, який рятує. 20% від кожної футболки йде на гуманітарку. {url}",
        "Футболка з історією. Козак – символ незламності. Замовити: {url}",
        "Зроби свій внесок у перемогу – обери футболку з козаком. {url}",
        "Твій вибір – допомога армії. Футболка з козаком та 20% на дрони. {url}",
        "Будь стильним та допомагай – футболка з козаком чекає на тебе. {url}"
    ],
    'ru': [
        "У меня есть футболка с казаком. 20% с продажи идёт на дроны и гуманитарку. Ссылка: {url}",
        "Кто ищет мерч? Футболка с украинским казаком, часть выручки перечисляю на помощь. {url}",
        "Поддержи Украину – купи футболку с казаком! 20% на дроны и гуманитарку. {url}",
        "Уникальный дизайн футболки с казаком. Каждая покупка приближает победу. Подробнее: {url}",
        "Футболка, которая объединяет. 20% от стоимости идёт нашим защитникам. Заказать: {url}",
        "Патриотическая одежда со смыслом. Донат на дроны с каждой футболкой. Ссылка: {url}",
        "Стань частью перемен – выбери футболку с казаком. 20% на помощь армии. {url}",
        "Одень патриотизм. Каждая футболка – это вклад в победу. Заказать здесь: {url}",
        "Уникальная футболка с казаком – подарок для себя или друга. 20% на ВСУ. {url}",
        "Присоединяйся к помощи – купи футболку с украинским казаком. {url}",
        "Мерч, который спасает. 20% от каждой футболки идёт на гуманитарку. {url}",
        "Футболка с историей. Казак – символ несокрушимости. Заказать: {url}",
        "Сделай свой вклад в победу – выбери футболку с казаком. {url}",
        "Твой выбор – помощь армии. Футболка с казаком и 20% на дроны. {url}",
        "Будь стильным и помогай – футболка с казаком ждёт тебя. {url}"
    ],
    'en': [
        "I have a t-shirt with a Ukrainian Cossack design. 20% of each sale goes to drones and humanitarian aid. Link: {url}",
        "Looking for Ukrainian merch? Check out this Cossack t-shirt. Part of the proceeds support the war effort. {url}",
        "Support Ukraine – buy a Cossack t-shirt! 20% goes to drones and humanitarian aid. {url}",
        "Unique Cossack t-shirt design. Every purchase brings victory closer. Details: {url}",
        "A t-shirt that unites. 20% of the cost goes to our defenders. Order here: {url}",
        "Patriotic clothing with a purpose. Donate to drones with every t-shirt. Link: {url}",
        "Be part of the change – choose the Cossack t-shirt. 20% to support the army. {url}",
        "Wear your patriotism. Every t-shirt is a contribution to victory. Order now: {url}",
        "Unique Cossack t-shirt – a gift for yourself or a friend. 20% to the Armed Forces. {url}",
        "Join the help – buy a Ukrainian Cossack t-shirt. {url}",
        "Merch that saves lives. 20% of every t-shirt goes to humanitarian aid. {url}",
        "A t-shirt with a story. The Cossack is a symbol of resilience. Order: {url}",
        "Make your contribution to victory – choose the Cossack t-shirt. {url}",
        "Your choice helps the army. Cossack t-shirt with 20% for drones. {url}",
        "Be stylish and help – the Cossack t-shirt is waiting for you. {url}"
    ]
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = TelegramClient('promo_session', API_ID, API_HASH)

def detect_language(text):
    t = text.lower()
    if any(c in t for c in ['укр', 'є', 'ї', 'і', 'мистецтво', 'графіті']):
        return 'uk'
    elif any(c in t for c in ['рус', 'ы', 'э', 'искусство', 'граффити']):
        return 'ru'
    else:
        return 'en'

def contains_keywords(text, lang):
    if not text:
        return False
    keywords = KEYWORDS.get(lang, KEYWORDS['en'])
    return any(kw in text.lower() for kw in keywords)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    try:
        if event.out:
            return
        comment_text = event.message.text or ''
        if not comment_text:
            return
        lang = detect_language(comment_text)
        if contains_keywords(comment_text, lang):
            answer = random.choice(ANSWERS[lang]).format(url=REDBUBBLE_URL)
            await event.respond(answer, comment_to=event.id)
            logger.info(f"Ответил в комментариях чата {event.chat_id} на сообщение {event.id}")
            return
        if event.is_reply:
            original_post = await event.get_reply_message()
            if original_post:
                original_text = original_post.text or ''
                lang_orig = detect_language(original_text)
                if contains_keywords(original_text, lang_orig):
                    answer = random.choice(ANSWERS[lang_orig]).format(url=REDBUBBLE_URL)
                    await event.respond(answer, comment_to=original_post.id)
                    logger.info(f"Ответил в комментариях чата {event.chat_id} на пост {original_post.id}")
    except Exception as e:
        logger.error(f"Ошибка в обработчике: {e}")

async def main():
    await client.start(phone=PHONE_NUMBER)
    logger.info("Бот запущен, слушаю сообщения и комментарии...")
    await client.send_message(MY_TELEGRAM_ID, "🚀 Промо-бот для Redbubble запущен!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
