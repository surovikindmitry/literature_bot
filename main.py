import asyncio
from aiogram import Bot, Dispatcher
from config import config
from handlers import start, help, description, publish

async def main():
    try:
        bot = Bot(token=config.BOT_TOKEN)
        dp = Dispatcher()

        dp.include_router(start.router)
        dp.include_router(help.router)
        dp.include_router(description.router)
        dp.include_router(publish.router)

        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
