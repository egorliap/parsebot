from aiogram.types import InlineKeyboardMarkup,InlineKeyboardButton, KeyboardButton,ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from scr.services.item_service import ItemInfo
import emoji

start_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Get started!",callback_data="start")]
])
marketplace_choice = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="WB",callback_data="wb")]
],resize_keyboard=True)
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Show all my products",callback_data="positions"),InlineKeyboardButton(text="Add new position",callback_data="add_new_position")]
])



async def item_menu(item:ItemInfo):
    kb = InlineKeyboardBuilder([
        [InlineKeyboardButton(text='Link',url=item.url),InlineKeyboardButton(text="Delete",callback_data=f"delete_{item.art}")],
        [InlineKeyboardButton(text=emoji.emojize(":left_arrow:"),callback_data="left"),InlineKeyboardButton(text=emoji.emojize(":right_arrow:"),callback_data="right")]
        ])
    return kb.adjust(2).as_markup()

async def item_updated_menu(item:ItemInfo):
    kb = InlineKeyboardBuilder([
        [InlineKeyboardButton(text='Link',url=item.url),InlineKeyboardButton(text="Delete",callback_data=f"delete_{item.art}")],
        ])
    return kb.adjust(2).as_markup()