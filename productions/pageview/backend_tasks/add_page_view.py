import asyncio
from aiohttp.web import Application
from aiohttp import ClientSession
from typing import Dict
from handles import (jianshu_add_page_view, csdn_add_page_view)

handles = {"jianshu": jianshu_add_page_view, "csdn": csdn_add_page_view}
interval = {
    "jianshu": 1,
    "csdn": 20,
}
session = ClientSession()


async def add_page_view(app: Application) -> None:
    while 1:
        try:
            tasks = [
                asyncio.ensure_future(
                    execute(
                        interval=interval[website_type],
                        website_values=website_values,
                        handle=handles[website_type]))
                for website_type, website_values in app["websites"].items()
            ]
            asyncio.gather(*tasks)
        except KeyError as e:
            await asyncio.sleep(5)
        finally:
            await asyncio.sleep(5)


async def execute(interval: int, website_values: dict, handle: object) -> None:
    for website_value in website_values:
        for i in website_value["articles"]:
            await asyncio.sleep(interval)
            await handle(session=session, url=i)