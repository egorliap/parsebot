from scr.database.base import Base
import datetime
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import (
    ForeignKey,
    BigInteger,
    text,
)

class User(Base):
    __tablename__ = "user"
    id:Mapped[int] = mapped_column(primary_key=True, unique=True,autoincrement=True)
    tg_id = mapped_column(BigInteger,unique=True,nullable=False)
    items:Mapped[list["Item_WB"]] = relationship(back_populates="user")


class Item_WB(Base):
    __tablename__ = "item_wb"
    id:Mapped[int] = mapped_column(unique=True,primary_key=True,autoincrement=True)
    url:Mapped[str]
    article=mapped_column(BigInteger,unique=True,nullable=False)
    last_check:Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    last_price:Mapped[float]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="items")

    
