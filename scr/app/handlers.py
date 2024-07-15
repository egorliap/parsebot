from aiogram.filters import CommandStart,Command
from aiogram.types import Message, CallbackQuery,ReplyKeyboardRemove,InputMediaPhoto
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Router, html, F

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
    await user.add_user_to_db()
    await callback.message.answer(text="OK! Now you can choose the options of menu",reply_markup=main_menu)
    await callback.message.delete()
    
@router.message(Command('menu'),)
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
    ii = ItemWBInterface()
    try:
        await ii.add_item_to_db(user_id=message.from_user.id,item_url=data.get('url',''))
        await state.clear()
        await message.answer(text="Added! Now we are tracking this product's price, you can compare it on 'Show all my products'")
    except:
        await message.answer(text="Something wrong with the url :(((((")
        
        
    
    

    





class Listing:
    def __init__(self,ui,main_callback) -> None:
        self.callback:CallbackQuery = main_callback
        self.ui:UserInterface = ui
        self.counter = 0
    async def show_first_position(self):
        items = self.ui.get_user_items()
        await self.callback.answer()
        try:
            item = await items.__anext__()
            self.message_ = await self.callback.message.answer_photo(
                        photo=item.img_url,
                        caption=f"{html.bold(item.title)}\n\nPrevious price: {item.prev_price} RUB\n\nCurrent price: {item.curr_price} RUB",
                        reply_markup=await item_menu(item),
                        )
        except StopAsyncIteration:
            self.message_ = await self.callback.message.edit_text(
                        text="You haven't added anything",
                        reply_markup=main_menu,
                        )
            return
        await self.callback.message.answer(
                        text="Here's the menu",
                        reply_markup=main_menu,
                        )
        self.items_iter = [item]
        async for el in items:
            self.items_iter.append(el)  

    async def show_next(self):
        self.counter+=1
        self.counter%=len(self.items_iter)
        item = self.items_iter[self.counter]
        file = InputMediaPhoto(media=item.img_url, caption=f"{html.bold(item.title)}\n\nPrevious price: {item.prev_price} RUB\n\nCurrent price: {item.curr_price} RUB")
        await self.message_.edit_media(
                media=file,
                reply_markup=await item_menu(item)
                )   
    async def show_previous(self):
        self.counter-=1
        self.counter%=len(self.items_iter)
        item = self.items_iter[self.counter]
        file = InputMediaPhoto(media=item.img_url, caption=f"{html.bold(item.title)}\n\nPrevious price: {item.prev_price} RUB\n\nCurrent price: {item.curr_price} RUB")
        await self.message_.edit_media(
                media=file,
                reply_markup=await item_menu(item)
                )
    async def delete_position(self,delete_callback:CallbackQuery):
        await self.ui.delete_item(delete_callback.data.split("_")[1])
        self.items_iter.pop(self.counter)
        self.counter -= 1
        if(len(self.items_iter)>0):
            await self.show_next()
        else:
            await self.message_.delete()
        
class ListingState(StatesGroup):
    listing:Listing = State()

    
    
@router.callback_query(F.data == 'positions')    
async def start_listing(callback:CallbackQuery,state:FSMContext):
    await callback.answer()
    listing = Listing(UserInterface(callback.from_user.id),callback)
    await state.set_state(ListingState.listing)
    await state.update_data(listing=listing)
    
    await listing.show_first_position()
    
@router.callback_query(F.data == "left")
async def prev_listing(callback:CallbackQuery,state:FSMContext):
    await callback.answer()
    data = await state.get_data()
    listing:Listing = data.get("listing",None)
    if(listing):
        await listing.show_previous()

@router.callback_query(F.data == "right")
async def next_listing(callback:CallbackQuery,state:FSMContext):
    await callback.answer()
    data = await state.get_data()
    listing:Listing = data.get("listing",None)
    if(listing):
        await listing.show_next()
        
@router.callback_query(F.data.startswith('delete_'))
async def delete_position(callback:CallbackQuery,state:FSMContext):
    await callback.answer()
    data = await state.get_data()
    listing:Listing = data.get("listing",None)
    if(listing):
        await listing.delete_position(callback)
        
        
