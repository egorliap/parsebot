from scr.database.models import User,Item_WB
from scr.database.base import session_factory 
from sqlalchemy import select


class UserInterface:
    def _check_user_in_db(self,id):
        with session_factory() as session:
            stmt = select(User).where(User.id == id)
            res = session.execute(statement=stmt)
            if(res.all()):
                return True
            else:
                return False
    def add_user_to_db(self,id):
        if(not(self._check_user_in_db(id))):
            with session_factory() as session:
                user = User(tg_id = id)
                session.add(user)
                session.commit()
            return True
        else:
            return False
