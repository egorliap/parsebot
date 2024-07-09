from aiogram.types import InlineKeyboardMarkup,InlineKeyboardButton, KeyboardButton,ReplyKeyboardMarkup

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

item_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Link",url="qweqweewqewqqwe"),InlineKeyboardButton(text="Delete",callback_data="delete_position")]
])