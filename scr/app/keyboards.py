from aiogram.types import InlineKeyboardMarkup,InlineKeyboardButton, KeyboardButton,ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from scr.services.item_service import ItemInfo

start_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Get started!",callback_data="start")]
])
marketplace_choice = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="WB",callback_data="wb")]
],resize_keyboard=True)
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Show all my positions",callback_data="positions"),InlineKeyboardButton(text="Add new position",callback_data="add_new_position")]
])
main_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Show all my positions",callback_data="positions"),KeyboardButton(text="Add new position",callback_data="add_new_position")]
])


async def item_menu(item:ItemInfo):
    kb = InlineKeyboardBuilder([
        [InlineKeyboardButton(text='Link',url=item.url),InlineKeyboardButton(text="Delete",callback_data=f"delete_{item.art}")]
        ])
    return kb.adjust(2).as_markup()
    