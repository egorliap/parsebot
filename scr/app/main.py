from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from scr.services.check_prices_service import PriceUpdater 
from scr.app.handlers import router


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


dp = Dispatcher()

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

async def main():


    price_updater = PriceUpdater()
    scheduler = AsyncIOScheduler()
    tr = IntervalTrigger(days=1)
    scheduler.add_job(func=price_updater.send_items,trigger=tr,args=[bot])
    scheduler.start()
    
    dp.include_router(router=router)
    await dp.start_polling(bot)
    

    
    
