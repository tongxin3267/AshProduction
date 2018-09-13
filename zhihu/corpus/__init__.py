import asyncio
from asyncio.queues import Queue
import ujson
from aiohttp import ClientSession
import parsel


class ZhihuCrawler:
    def __init__(self, a_num: int = 10, b_num: int = 10):
        self.a_num = a_num
        self.b_num = b_num
        self.newest_tasks_queue = Queue()
        self.waiting_tasks_queue = Queue()
        self.session_list = [ClientSession() for _ in range(self.a_num)]
        self.explore_url = "https://www.zhihu.com/node/ExploreRecommendListV2"
        self.headers = {
            "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0",
            "X-Requested-With": "XMLHttpRequest",
            "X-Xsrftoken": "ee0a6b78a7392e789fc6454d9d3c0c3e",
            "Host": "www.zhihu.com",
            "Referer": "https://www.zhihu.com/explore/recommendations",
            "TE": "Trailers",
            "Cookie": 'd_c0="ACAncWQU4A2PTt0dDx5NSdiXBS5oOcFFnf4=|1531156030"; q_c1=9d091f84d1cf4b1f91696cbf0b3611ad|1536808006000|1531156030000; _zap=83244458-c0ab-46b1-a3cc-536981defe85; z_c0="2|1:0|10:1531156201|4:z_c0|92:Mi4xRXJBVUFnQUFBQUFBSUNkeFpCVGdEU1lBQUFCZ0FsVk42ZVF3WEFEdGd2QTQ4cnVyUjE5a3dHMl92OW1KS3BrRTNR|612c61ffe1c5008a363669bf0ab29cb6b2019db5cee798ec5b87e007ee5e3a93"; tgw_l7_route=200d77f3369d188920b797ddf09ec8d1; _xsrf=ee0a6b78a7392e789fc6454d9d3c0c3e'
        }
        self.params = {"method": "next", "params": ujson.dumps({'limit': 20, 'offset': 20})}

    async def a(self, session: ClientSession):
        while 1:
            data = await self.newest_tasks_queue.get()
            data = ujson.loads(data)
            response = await session.get(url=data["url"], params=self.params)
            print(await response.text())
            await self.waiting_tasks_queue.put(await response.text())

    async def b(self, content: str):
        while 1:
            data = await self.waiting_tasks_queue.get()
            print(data)
            # response = await session.get(data)
            # await self.newest_tasks_queue.put()
    async def run(self):
        data = {"url": self.explore_url}
        await self.newest_tasks_queue.put(ujson.dumps(data))
        ass = [
            asyncio.ensure_future(self.a(session=session))
            for session in self.session_list
        ]
        await asyncio.gather(*ass)
        bss = [asyncio.ensure_future(self.b()) for _ in range(self.b_num)]
        await asyncio.gather(*bss)