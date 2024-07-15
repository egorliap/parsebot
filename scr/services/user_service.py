from typing import List
from scr.database.models import User
from scr.database.base import session_factory 
from .item_service import ItemWBInterface,ItemInfo
from sqlalchemy import select


class UserInterface:
    def __init__(self,tg_id) -> None:
        self.id = tg_id
    async def _check_user_in_db(self):
        async with session_factory() as session:
            stmt = select(User).where(User.tg_id == self.id)
            res = await session.execute(statement=stmt)
            if(res.all()):
                print(res.all())
                return True
            else:
                return False
    async def add_user_to_db(self):
        if(not(await self._check_user_in_db())):
            async with session_factory() as session:
                user = User(tg_id = self.id)
                session.add(user)
                await session.commit()
            
        
        
    def get_user_items(self):
        return ItemWBInterface().get_all_user_items(self.id)
    
    
    async def delete_item(self,article):
        await ItemWBInterface().delete_item(art=article,user_id= self.id)
