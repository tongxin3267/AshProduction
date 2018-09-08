# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     AshProduction add_page_views
   Description :
   Author :       SamariaLin
   date：          2018/9/8
-------------------------------------------------
   Change Activity:
                   2018/9/8:
-------------------------------------------------
"""
__author__ = 'LateautunmLin'

import asyncio
import random
from typing import List
import aiohttp
from parsel import Selector
from asyncio.queues import Queue

#type hint
Session = aiohttp.ClientSession
UserId = str
Article_list = List[str]

class JianshuPageView:
    def __init__(self):
        self.user_article_list_temp = f"https://www.jianshu.com/u/%s?order_by=shared_at&page=%s"
        self.primary_page_num = 2
        self.max_page_num = 1000
        self.random_sleep = (3,5)
        self.worker_num = 10
    async def add_page_views(self,url_sub:str,session:Session):
        data = {
            "uuid":"5e43e1c6-ca97-4787-a033asddasd",
            "referrer":"https://www.jianshu.com"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0",
            "X-CSRF-Token": "+LOfEEblhHerUy77qZvhhWkwiUIYrirND0ofIfYesBLc0WUIhsHwFTTzmE+jprN8Yto50LE79knh3Ao8oq30vg==",
            "Cookie": "sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22164f0ee834e42a-06c76e6f7944b38-4c312b7b-1327104-164f0ee834f2ab%22%2C%22%24device_id%22%3A%22164f0ee834e42a-06c76e6f7944b38-4c312b7b-1327104-164f0ee834f2ab%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.baidu.com%2Flink%22%2C%22%24latest_referrer_host%22%3A%22www.baidu.com%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%7D%2C%22first_id%22%3A%22%22%7D; read_mode=day; default_font=font2; locale=zh-CN; _m7e_session=920bfd266a5d73adf6bff486082f84e4; signin_redirect=https%3A%2F%2Fwww.jianshu.com%2Fp%2F4a526bc6276b",
            "Host": "www.jianshu.com",
            "Referer":f"https://www.jianshu.com/p/{url_sub}",
        }
        url = f"https://www.jianshu.com/notes/{url_sub}/mark_viewed.json"
        async with session.post(url,headers=headers,data=data) as response:
            print(await response.text())
    async def worker(self):
        session = aiohttp.ClientSession()
        while 1:
            try:
                data = await self.task_queue.get()
                await self.add_page_views(url_sub=data,session=session)
            except Exception as e:
                print(e)
            await asyncio.sleep(1)
    async def get_user_article(self,userId:UserId,page_number:int):
        async with aiohttp.ClientSession() as session:
            url = self.user_article_list_temp%(userId,page_number)
            async with session.get(url=url) as response:
                content = await response.text()
                dom = Selector(text=content)
                article_list = dom.xpath("//a[@class='title']/@href").getall()
                return article_list
    async def produer(self,article_list:Article_list):
        while 1:
            for article_id in article_list:
                await self.task_queue.put(article_id.split("/")[-1])
            await asyncio.sleep(random.randint(*self.random_sleep))
    async def run(self,*args,**kwargs):
        self.task_queue = Queue()
        userId = kwargs.get("userId",None)
        if not userId:
            raise Exception
        temp_page_article_lists = []
        full_article_lists = []
        for page in range(self.primary_page_num,self.max_page_num):
            current_page_article_lists = await self.get_user_article(userId=userId,page_number=page)
            if current_page_article_lists==temp_page_article_lists:
                break
            else:
                temp_page_article_lists = current_page_article_lists
                full_article_lists.extend(current_page_article_lists)
        asyncio.ensure_future(self.produer(article_list=full_article_lists))
        tasks = [
            asyncio.ensure_future(self.worker()
            ) for _ in range(self.worker_num)
        ]
        await asyncio.gather(*tasks)
if __name__ == "__main__":
    d = JianshuPageView()
    l =asyncio.get_event_loop()
    l.run_until_complete(d.run(userId="e9fdf09df277"))