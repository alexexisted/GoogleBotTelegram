import asyncio
from aiogram import Bot, F, Dispatcher

import executor as executor
from google.oauth2 import service_account
import googleapiclient.discovery

import logging
import sys

import secure
from handlers.addEvent import addCalendarEvent
from handlers.startFunc import startButton
from handlers.watchTime import watchCalendarTime

# Инициализация сервисного аккаунта Google
credentials = service_account.Credentials.from_service_account_file('creds1.json') #передаем файл нужный для авторизации
service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

async def main():
    bot = Bot(secure.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_routers(startButton.router, addCalendarEvent.router, watchCalendarTime.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

# Запуск бота
if __name__ == '__main__':
    # router.start_polling(router, skip_updates=True)
    # logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    asyncio.run(main())