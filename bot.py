import asyncio
from aiogram import Bot, F, Dispatcher
import secure
from handlers.addEvent import addCalendarEvent
from handlers.startFunc import startButton
from handlers.watchTime import watchCalendarTime
from handlers.deleteEvent import deleteCalendarEvent


async def main():
    bot = Bot(secure.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_routers(startButton.router, addCalendarEvent.router, watchCalendarTime.router, deleteCalendarEvent.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

# Запуск бота
if __name__ == '__main__':
    # logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    asyncio.run(main())