import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from router import router, get_formatted, repository, get_db, Session
from database import database

database.Base.metadata.create_all(bind=database.engine)


async def scheduled_job(bot: Bot, db: Session = get_db()):
    users_id = repository.get_users_id(db)
    formatted_result = get_formatted()
    for i in users_id:
        await bot.send_message(i, formatted_result, parse_mode=ParseMode.MARKDOWN)


async def main():
    bot = Bot(token="6366785760:AAHGF2ayus90M7nmmCcKXEybKgL0MfRs99A", parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    scheduler = AsyncIOScheduler(timezone="Asia/Almaty")

    scheduler.add_job(scheduled_job, trigger='interval', hours=24, kwargs={'bot': bot})
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
