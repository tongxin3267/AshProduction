# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     AshProduction add_page_views
   Description :
   Author :      LateautunmLin 
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

# type hint
Session = aiohttp.ClientSession
UserId = str
Article_list = List[str]


class CSDNPageView:
    def __init__(self):
        self.personal_homepage_prefix = "https://blog.csdn.net/"
        self.personal_homepage_part = "/article/list/"
        self.primary_page_num = 0
        self.max_page_num = 1000
        self.wait_frequency = 1
        # 大概需要1分钟以上间隔对于同一IP来说
        self.random_sleep = (80, 100)
        self.worker_num = 1

    async def add_page_views(self, url: str, session: Session) -> None:
        """
        According to different articlesID structure request. 
        there are some optimization
        """
        headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0",
            "Origin":
            "https://blog.csdn.net",
        }
        try:
            print(url)
            await session.get(url, headers=headers)
        except Exception:
            # Todo
            pass

    async def worker(self) -> None:
        """
        Loop to get ID and use post request. 
        """
        session = aiohttp.ClientSession()
        while 1:
            try:
                data = await self.task_queue.get()
                await self.add_page_views(url=data, session=session)
            except Exception as e:
                print(e)
            await asyncio.sleep(delay=self.wait_frequency)

    async def get_user_article(self, userId: UserId,
                               page_number: int) -> Article_list:
        async with aiohttp.ClientSession() as session:
            url = f"{self.personal_homepage_prefix}{userId}{self.personal_homepage_part}{page_number}"
            async with session.get(url=url) as response:
                content = await response.text()
                dom = Selector(text=content)
                article_list = dom.xpath("//h4[@class='']/a/@href").getall()
                return article_list

    async def producer(self, article_list: Article_list) -> None:
        while 1:
            for article_url in article_list:
                await self.task_queue.put(article_url)
            await asyncio.sleep(random.randint(*self.random_sleep))

    async def run(self, *args, **kwargs) -> None:
        """
        add_page_view module common execute entry
        """
        self.task_queue = Queue()
        userId = kwargs.get("userId", None)
        articleId = kwargs.get("articleId", None)
        if not userId and not articleId:
            raise Exception
        full_article_lists = []
        if articleId:
            full_article_lists = [articleId] if isinstance(articleId,
                                                           str) else articleId
        else:
            for page in range(self.primary_page_num, self.max_page_num):
                current_page_article_lists = await self.get_user_article(
                    userId=userId, page_number=page)
                if not current_page_article_lists:
                    break
                else:
                    full_article_lists.extend(current_page_article_lists)
        asyncio.ensure_future(self.producer(article_list=full_article_lists))
        tasks = [
            asyncio.ensure_future(self.worker())
            for _ in range(self.worker_num)
        ]
        await asyncio.gather(*tasks)