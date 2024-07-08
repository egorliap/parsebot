from scr.database.models import Item_WB
from scr.database.base import session_factory 
from scr.database.config import HEADERS_WB
import json
from sqlalchemy import select
import requests

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
    
    
class ItemWBInterface(ItemInterface):
    wb_server_id_ranges = [143,287,431,719,1007,1061,1115,1169,1313,1601,1655,1919,2045,2189,2405,2621]
    def _get_article_from_url(self,item_url)->str:
        inds = []
        for i in range(len(item_url)):
            if item_url[i] == "/":
                inds.append(i)
        art = item_url[inds[-2]+1:inds[-1]]
        return art
        
    def _check_existance(self, item_url)-> bool:
        art = self._get_article_from_url(item_url)
        session_http = requests.Session()
        session_http.headers.update(HEADERS_WB) 
        session_http.headers.update({
            'Referer': item_url
            })
        response = session_http.get(
                "https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=12358470&spp=30&nm=" + art)  
        if(response.status_code == 200 and art):
            return True 
        return False
    
    def _get_previous_price(self, item_id)->float:
        with session_factory() as session:
            q = select(Item_WB.last_price).filter_by(id=item_id)
            res = session.execute(q)
            return res.scalars().one()
    
    def _get_products_list(self,item_url):
        session_http = requests.Session()
        session_http.headers.update(HEADERS_WB) 
        session_http.headers.update({
            'Referer': item_url
            })
        response = json.loads(
            session_http.get(
                "https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=12358470&spp=30&nm=" + self._get_article_from_url(item_url))
            .content)    
        products = response.get('data','data_not_found').get('products','products_not_found')
        return products
    
    def _get_current_price(self, item_url)->float:
        products = self._get_products_list(item_url)
        if(products):
            sizes = products[0].get('sizes','sizes_not_found')
            prices = sizes[0].get('price',-1)
            price = prices.get('product','product_not_found')/100
        else:
            price = -1
            print("Products are not awailaible")        
        return price
        
    def _get_main_image_url(self,item_url)->str:
        art = self._get_article_from_url(item_url)
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
    
    def _get_title(self,item_url)->str:
        products = self._get_products_list(item_url)
        if products:
            return products[0].get('name','name_not_found')
        return ''
    
    def add_item_to_db(self, user_id, item_url)-> bool:
        if(not(self._check_existance(item_url))):
            return False
        price = self._get_current_price(item_url)
        if(price == -1):
            return False
        item = Item_WB(url=item_url,article=int(self._get_article_from_url(item_url)),last_price=price,user_id=user_id)
        with session_factory() as session:
            session.add(item)
            session.commit()
        return True
        
    
    def get_price_update_message(self,item_url)-> dict:
        """{
            title:str
            prev_price:float
            curr_price:float
            img_url:str
            }"""
        