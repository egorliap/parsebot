from scr.database.models import Item_WB
from scr.database.base import session_factory 
from scr.database.config import HEADERS_WB
import json
from sqlalchemy import select,delete
import requests
import aiohttp
from aiohttp import ClientSession

class ItemInterface:
    def _check_existance(self, item_url)-> bool:
        pass
    def _get_previous_price(self, item_url)->float:
        pass
    def _get_current_price(self, item_url)->float:
        pass
    def _get_main_image_url(self,item_url)->str:
        pass
    def add_item_to_db(self, item_url)-> bool:
        pass
    def deliver_price_update(self):
        pass
    
    
class ItemWBInterface:
    wb_server_id_ranges = [143,287,431,719,1007,1061,1115,1169,1313,1601,1655,1919,2045,2189,2405,2621]
    
    def _get_article_from_url(self,item_url)->str:
        inds = []
        for i in range(len(item_url)):
            if item_url[i] == "/":
                inds.append(i)
        if(len(inds)>=2):
            art = item_url[inds[-2]+1:inds[-1]]
        else:
            art = ''
        return art
        
    async def _check_existance(self, item_url,session_http:ClientSession)-> bool:
        art = self._get_article_from_url(item_url)
        
        async with session_http.get(
            "https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=12358470&spp=30&nm="
            + 
            art) as response:
            if(response.status == 200 and art):
                return True 
            return False
    
    
    
    async def _get_products_list(self,item_url,session_http:ClientSession):
        
        async with session_http.get(
                "https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=12358470&spp=30&nm="
                + self._get_article_from_url(item_url)) as response:
            response = json.loads(await response.text())
            products = response.get('data','data_not_found').get('products','products_not_found')
            return products
        
    async def _get_previous_price(self, article:int)->float:
        async with session_factory() as session:
            q = select(Item_WB.last_price).filter_by(article=article)
            res = await session.execute(q)
            return res.scalars().one()
        
    async def _get_current_price(self, item_url,session_http)->float:
        products = await self._get_products_list(item_url,session_http)
        if(products):
            sizes = products[0].get('sizes','sizes_not_found')
            prices = sizes[0].get('price',-1)
            price = prices.get('product','product_not_found')/100
        else:
            price = -1
            print("Products are not awailaible")        
        return price
        
    def _get_main_image_url(self,art:str)->str:
        vol = int(art[:-5])
        basket = '17'
        for i in range(len(self.wb_server_id_ranges)):
            if(self.wb_server_id_ranges[i]>= vol):
                basket = str(i+1)
                if(len(basket) == 1):
                    basket = "0" + basket
                break
        url = f"https://basket-{basket}.wbbasket.ru/vol{art[:-5]}/part{art[:-3]}/{art}/images/big/1.webp"
        return url
    
    async def _get_title(self,item_url,session_http)->str:
        products = await self._get_products_list(item_url,session_http)
        if products:
            return products[0].get('name','name_not_found')
        return ''
    
    
    
    async def add_item_to_db(self, user_id, item_url)-> bool:
     
        
        async with ClientSession(headers=HEADERS_WB.update({'Referer': item_url})) as session_http:
            if(not(await self._check_existance(item_url,session_http=session_http))):
                return False
            price = await self._get_current_price(item_url,session_http=session_http)
            if(price == -1):
                return False
            item = Item_WB(url=item_url,
                        article=int(self._get_article_from_url(item_url)),
                        last_price=price,
                        user_id=user_id)
            async with session_factory() as session:
                session.add(item)
                await session.commit()
            return True
        
    
    
    async def get_price_update_message(self,item_url)-> dict:
      
        async with ClientSession(headers=HEADERS_WB.update({'Referer': item_url})) as session_http:
            if(not(self._check_existance(item_url,session_http))):
                return None
            prev_price = await self._get_previous_price(item_url)
            curr_price = await self._get_current_price(item_url,session_http)
            if(curr_price == -1):
                return None
            img_url = self._get_main_image_url(self._get_article_from_url(item_url))
            title = await self._get_title(item_url,session_http)
            return ItemInfo(
                    title=title,
                    prev_price=prev_price,
                    curr_price=curr_price,
                    img_url=img_url,
                    url=item_url,
                    )
        
        
    async def get_all_user_items(self,user_id):
        
        query = select(Item_WB).filter_by(user_id=user_id)
        async with session_factory() as session:
            res = await session.execute(query)
            ans = res.scalars().all()
        items = []
        session_http = ClientSession()
        session_http.headers.update(HEADERS_WB) 
        for item in ans:
            session_http.headers.update({
                'Referer': item.url
                })
            
            items.append(ItemInfo(
                    title=await self._get_title(item.url,session_http),
                    prev_price=await self._get_previous_price(item.article),
                    curr_price=await self._get_current_price(item.url,session_http),
                    img_url=self._get_main_image_url(str(item.article)),
                    url=item.url,
                    article=item.article
                    ))
        await session_http.close()
        return items
    
    
    async def delete_item(self,art, user_id):
        q = delete(Item_WB).filter_by(article = int(art),user_id = user_id)
        async with session_factory() as session:
            await session.execute(q)
            await session.commit()
        


        
class ItemInfo:
    def __init__(self,title:str,prev_price:float,curr_price:float,img_url:str,url:str,article:str) -> None:
        self.title = title
        self.prev_price = prev_price
        self.curr_price = curr_price
        self.img_url = img_url
        self.url = url
        self.art = article
    