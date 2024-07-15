from aiogram import html
from scr.app.keyboards import item_menu, item_updated_menu
from scr.database.config import HEADERS_WB
from scr.database.models import Item_WB
from .item_service import ItemWBInterface
from aiohttp import ClientSession
from sqlalchemy import func,update
from typing import List

class PriceUpdater:
    def __init__(self):
        self.interface = ItemWBInterface()
    async def _compare_prices(self,item:Item_WB,session_http: ClientSession)->bool:
        """Сравнивает текущую и предыдущую цены, в случае, если текущая меньше предыдущей на 20%, возвращает True"""
        
        curr_price = await self.interface.get_current_price(item.url,session_http)
        if(curr_price <= item.last_price*4/5):
            return True
        return False
    
    
    async def filter_items(self)->List[Item_WB]:
        session = ClientSession()
        ans = []
        items = await self.interface.get_items_checked_in_period()
        for item in items:
            if(await self._compare_prices(item,session)):
                ans.append(item)
        await session.close()
        return ans


    async def send_items(self,bot):
        session_http = ClientSession()
        session_http.headers.update(HEADERS_WB) 
        filtered_items = await self.filter_items()
        for item_ in filtered_items:
            item =  await self.interface.create_info_message(item_,session_http)
            await self.interface.update_price_info(item_)
            print(f"\n\n\nSending to {item.user_id=}\n\n")

            await bot.send_photo(chat_id=item.user_id,
                            photo=item.img_url,
                            caption=f"{html.bold(item.title)}\n\nPrevious price: {item.prev_price} RUB\n\nCurrent price: {item.curr_price} RUB",
                            reply_markup=await item_updated_menu(item),
                            )
        await session_http.close()