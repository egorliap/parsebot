from typing import List
from scr.database.models import User
from scr.database.base import session_factory 
from .item_service import ItemWBInterface,ItemInfo
from sqlalchemy import select


class UserInterface:
    def __init__(self,tg_id) -> None:
        self.id = tg_id
    def _check_user_in_db(self):
        with session_factory() as session:
            stmt = select(User).where(User.tg_id == self.id)
            res = session.execute(statement=stmt)
            if(res.all()):
                print(res.all())
                return True
            else:
                return False
    def add_user_to_db(self):
        if(not(self._check_user_in_db())):
            with session_factory() as session:
                user = User(tg_id = self.id)
                session.add(user)
                session.commit()
            return True
        else:
            return False
        
        
    def get_user_items(self)->List[ItemInfo]:
        return ItemWBInterface().get_all_user_items(self.id)
    
    
    def delete_item(self,article):
        ItemWBInterface().delete_item(art=article,user_id= self.id)
