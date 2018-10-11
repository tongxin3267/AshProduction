# -*- coding: utf-8 -*-
'''
------------------------------------------------------------
File Name: auto_discovery_new.py
Description : 
Project: backend_tasks
Last Modified: Thursday, 11th October 2018 2:22:29 pm
-------------------------------------------------------------
'''
import asyncio
from aiohttp.web import Application
from handles import (jianshu_lst, csdn_lst)


async def auto_discovery_new(app: Application) -> None:
    while 1:
        tasks = [asyncio.ensure_future(refresh_articles(
            app=app, website=k, uid=user
        ))
            for k, v in app["websites"].items() for user in v
        ]
        asyncio.gather(*tasks)
        await asyncio.sleep(3600)


async def refresh_articles(app: Application, website: str, uid: str) -> None:
    handles = {"jianshu": jianshu_lst, "csdn": csdn_lst}
    news = await handles[website](pages=10, uid=uid)
    app["websites"][website][uid] = news
