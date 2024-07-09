from scr.services.user_service import *
from scr.services.item_service import *

from scr.app.keyboards import *

from aiogram import Bot, Dispatcher, html,F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart,Command
from aiogram.types import Message, CallbackQuery,ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import asyncio

from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()


class AddPosition(StatesGroup):
    marketplace = State()
    url = State()

@dp.message(CommandStart())
async def start(message:Message):
    
    ans = f"Hello, {html.bold(message.from_user.full_name)}!\nThis bot is supposed to be used in the way of weekly checking price update on russian marketplaces (WB,...)\nTo get started, press the button and choose marketplace. Then, send the URL of desired item on chosen marketplace"
    await message.answer(ans,
                         reply_markup=start_menu)
    
@dp.callback_query(F.data == 'start')
async def reg(callback: CallbackQuery):
    await callback.answer()
    
    ui = UserInterface()
    ui.add_user_to_db(int(callback.from_user.id))
    await callback.message.edit_text(text="OK! Choose option:")
    await callback.message.edit_reply_markup(reply_markup=main_menu)
@dp.message(Command('menu'))
async def show_menu(message:Message):
    await message.answer(text="Here is the menu",reply_markup=main_menu)


    
    
@dp.callback_query(F.data == 'add_new_position')
async def choose_mp(callback:CallbackQuery,state:FSMContext):
    await callback.answer()
    await state.set_state(AddPosition.marketplace)
    await callback.message.answer(text="Choose desired marketplace",reply_markup=marketplace_choice)

@dp.message(AddPosition.marketplace)
async def get_url(message:Message,state:FSMContext):
    await state.update_data(marketplace = message.text)
    await state.set_state(AddPosition.url)

    await message.answer(text = "Now, enter URL of the desired item",reply_markup=ReplyKeyboardRemove())
    
@dp.message(AddPosition.url)
async def finish_addition(message:Message,state:FSMContext):
    await state.update_data(url = message.text)
    data = await state.get_data()
    await message.reply(text=f"MP: {data['marketplace']}, url: {data['url']}")
    ii = ItemWBInterface()
    ii.add_item_to_db(user_id=message.from_user.id,item_url=data['url'])
    await state.clear()


@dp.callback_query(F.data == 'positions')
async def show_positions(callback:CallbackQuery):
    ii = ItemWBInterface()
    items = ii.get_all_user_items(callback.from_user.id)
    await callback.answer()
    for item in items:
        await callback.message.answer_photo(
            photo=item['img_url'],
            caption=f"{html.bold(item['title'])}\n\nURL: {item['item_url']}\n\nCurrent price: {item['price']} RUB"
            )
    
    


async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)
