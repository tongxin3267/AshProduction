import asyncio
from aiohttp.web import Application
from aiohttp import ClientSession
from typing import Dict
from handles import (jianshu_add_page_view, csdn_add_page_view)

handles = {"jianshu": jianshu_add_page_view, "csdn": csdn_add_page_view}
session = ClientSession()


async def add_page_view(app: Application) -> None:
    while 1:
        try:
            for website_type, website_values in app["websites"].items():
                for website_value in website_values:
                    for i in website_value["articles"]:
                        # await asyncio.sleep(20)
                        await handles[website_type](session=session, url=i)
        except KeyError as e:
            pass
        await asyncio.sleep(0.1)