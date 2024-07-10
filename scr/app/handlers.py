from aiogram.filters import CommandStart,Command
from aiogram.types import Message, CallbackQuery,ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Router, html, F
import asyncio

from scr.services.user_service import *
from scr.services.item_service import *
from scr.app.keyboards import *

router = Router()

class AddPosition(StatesGroup):
    marketplace = State()
    url = State()

@router.message(CommandStart())
async def start(message:Message):
    ans = f"Hello, {html.bold(message.from_user.full_name)}!\nThis bot is supposed to be used in the way of weekly checking price update on russian marketplaces (WB,...)\nTo get started, press the button and choose marketplace. Then, send the URL of desired item on chosen marketplace"
    await message.answer(ans,
                         reply_markup=start_menu)
    
    
    
@router.callback_query(F.data == 'start')
async def reg(callback: CallbackQuery):
    user = UserInterface(callback.from_user.id)
    user.add_user_to_db()
    await callback.answer()
    await callback.message.edit_text(text="OK! Choose option:")
    await callback.message.edit_reply_markup(reply_markup=main_menu)
    
@router.message(Command('menu'))
async def show_menu(message:Message):
    await message.answer(text="Here is the menu",reply_markup=main_menu)


    
    
    
    
    
    
@router.callback_query(F.data == 'add_new_position')
async def choose_mp(callback:CallbackQuery,state:FSMContext):
    await callback.answer()
    await state.set_state(AddPosition.marketplace)
    await callback.message.answer(text="Choose desired marketplace",reply_markup=marketplace_choice)

@router.message(AddPosition.marketplace)
async def get_url(message:Message,state:FSMContext):
    await state.update_data(marketplace = message.text)
    await state.set_state(AddPosition.url)

    await message.answer(text = "Now, enter URL of the desired item",reply_markup=ReplyKeyboardRemove())
    
@router.message(AddPosition.url)
async def finish_addition(message:Message,state:FSMContext):
    await state.update_data(url = message.text)
    data = await state.get_data()
    await message.reply(text=f"MP: {data['marketplace']}, url: {data['url']}")
    ii = ItemWBInterface()
    ii.add_item_to_db(user_id=message.from_user.id,item_url=data['url'])
    await state.clear()


@router.callback_query(F.data.startswith('delete_'))
async def delete_position(callback:CallbackQuery):
    await callback.answer()
    interface = UserInterface(callback.from_user.id)
    interface.delete_item(callback.data.split("_")[1])




@router.callback_query(F.data == 'positions')
async def show_positions(callback:CallbackQuery):
    user = UserInterface(callback.from_user.id)
    items = user.get_user_items()
    mgs = []
    for item in items:
        await callback.message.answer_photo(
            photo=item.img_url,
            caption=f"{html.bold(item.title)}\n\nPrevious price: {item.prev_price} RUB\n\nCurrent price: {item.curr_price} RUB",
            reply_markup=await item_menu(item),
            )
    await callback.message.answer(text="Here is the menu",reply_markup=main_menu)
    await callback.answer()
    
    