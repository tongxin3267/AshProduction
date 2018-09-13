from typing import Dict, List
import asyncio
from asyncio.locks import Lock
from asyncio.queues import Queue
import ujson
from aiohttp import ClientSession
from aiohttp.client_exceptions import ContentTypeError
import re
from parsel import Selector

Params = Dict[str, str]
Sessions = List[ClientSession]
ListData = Dict[str, List or str]


class ZhihuCrawler:
    def __init__(self, request_worker_num: int = 10, parser_worker_num: int = 1):
        self.request_worker_num = request_worker_num
        self.parser_worker_num = parser_worker_num
        self.newest_tasks_queue = Queue()
        self.waiting_tasks_queue = Queue()
        self._session_list = None
        self.explore_url = "https://www.zhihu.com/node/ExploreRecommendListV2"
        self.lheaders = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0",
            "X-Requested-With": "XMLHttpRequest",
            "X-Xsrftoken": "ee0a6b78a7392e789fc6454d9d3c0c3e",
            "Host": "www.zhihu.com",
            "Referer": "https://www.zhihu.com/explore/recommendations",
            "TE": "Trailers",
            "Cookie": 'd_c0="ACAncWQU4A2PTt0dDx5NSdiXBS5oOcFFnf4=|1531156030"; q_c1=9d091f84d1cf4b1f91696cbf0b3611ad|1536808006000|1531156030000; _zap=83244458-c0ab-46b1-a3cc-536981defe85; z_c0="2|1:0|10:1531156201|4:z_c0|92:Mi4xRXJBVUFnQUFBQUFBSUNkeFpCVGdEU1lBQUFCZ0FsVk42ZVF3WEFEdGd2QTQ4cnVyUjE5a3dHMl92OW1KS3BrRTNR|612c61ffe1c5008a363669bf0ab29cb6b2019db5cee798ec5b87e007ee5e3a93"; tgw_l7_route=200d77f3369d188920b797ddf09ec8d1; _xsrf=ee0a6b78a7392e789fc6454d9d3c0c3e'
        }
        self.pheaders = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0",
            "TE": "Trailers",
            "Cookie": 'd_c0="AHBmNNN83w2PTgvclkUS7xI_MOb0X9HDwS8=|1531116298"; q_c1=1a989d1794dc4f3f9835e88abfdce482|1536810135000|1531116298000; _zap=0a4a228c-c224-4d41-8603-f88fefa9271a; l_cap_id="OTQ3ZjI5NmI0ZDZjNDYxYjkxMDczNjQ3NmE0ZTg2YWY=|1536813804|6c91c2d0c853173aeb38c4e763e6a3b233f8af2c"; r_cap_id="YTFhOWIwYTRkZDBmNDU1YjhjMjllZmQ3MzY2MTVlYmQ=|1536813804|fed4407138795e99d72e675af96415d2f034f61f"; cap_id="MTE1ZjhmMDI3MDFmNGU2NTk0YzA4YWJhZmVhM2VlYjI=|1536813804|c570582919a1cde09b1072fd5366e368ceb07b07"; l_n_c=1; n_c=1; _xsrf=1JF13JCfRtndqZRThXVrQEINC38zvfGR; capsion_ticket="2|1:0|10:1536812018|14:capsion_ticket|44:ZTE3MGNiZmFhY2QzNDg3MDgwOTA3N2VhOTViNTQ2ZTE=|60b884c70c138169d211000d8450beb115985497fd4f0c929aa660e8576f2177"; tgw_l7_route=69f52e0ac392bb43ffb22fc18a173ee6'
        }
        self.cheaders = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0",
            "Host": "www.zhihu.com",
            "Cookie": 'd_c0="AHBmNNN83w2PTgvclkUS7xI_MOb0X9HDwS8=|1531116298"; q_c1=1a989d1794dc4f3f9835e88abfdce482|1536810135000|1531116298000; _zap=0a4a228c-c224-4d41-8603-f88fefa9271a; l_cap_id="OTQ3ZjI5NmI0ZDZjNDYxYjkxMDczNjQ3NmE0ZTg2YWY=|1536813804|6c91c2d0c853173aeb38c4e763e6a3b233f8af2c"; r_cap_id="YTFhOWIwYTRkZDBmNDU1YjhjMjllZmQ3MzY2MTVlYmQ=|1536813804|fed4407138795e99d72e675af96415d2f034f61f"; cap_id="MTE1ZjhmMDI3MDFmNGU2NTk0YzA4YWJhZmVhM2VlYjI=|1536813804|c570582919a1cde09b1072fd5366e368ceb07b07"; l_n_c=1; _xsrf=dba45503a51bd0f6a6d8053c62b8f554; n_c=1; _xsrf=1JF13JCfRtndqZRThXVrQEINC38zvfGR; capsion_ticket="2|1:0|10:1536812018|14:capsion_ticket|44:ZTE3MGNiZmFhY2QzNDg3MDgwOTA3N2VhOTViNTQ2ZTE=|60b884c70c138169d211000d8450beb115985497fd4f0c929aa660e8576f2177"'
        }
        self.offset = 0
        self.offset_lock = Lock()
        self.comment_url_temp = f"https://www.zhihu.com/r/posts/%s/comments"

    @property
    def params(self) -> Params:
        return {
            "method": "next",
            "params": ujson.dumps(
                {'limit': 20, 'offset': self.offset})
        }

    @property
    def sessions(self) -> Sessions:
        if self._session_list is None:
            self._session_list = [ClientSession()
                                  for _ in range(self.request_worker_num)]
        return self._session_list

    async def package_list_task(self) -> None:
        data = {
            "type": "list",
            "url": self.explore_url
        }
        await self.newest_tasks_queue.put(data)

    async def request_worker(self, session: ClientSession) -> None:
        while 1:
            newest_task = await self.newest_tasks_queue.get()
            if newest_task["type"] == "list":
                async with self.offset_lock:
                    self.offset += 20
                response = await session.post(url=newest_task["url"], headers=self.lheaders, data=self.params)
                json_data = await response.json()
                data = {
                    "type": "list",
                    "data": json_data
                }
            elif newest_task["type"] == "post":
                response = await session.get(headers=self.pheaders, url=newest_task["url"])
                text_data = await response.text()
                data = {
                    "type": "post",
                    "data": text_data
                }
            elif newest_task["type"] == "comment":
                print(newest_task)
                response = await session.get(headers=self.cheaders, url=newest_task["url"])
                try:
                    json_data = await response.json()
                except ContentTypeError:
                    continue
                data = {
                    "type": "comment",
                    "data": json_data
                }
            await self.waiting_tasks_queue.put(data)

    async def parser_worker(self) -> None:
        while 1:
            datas = await self.waiting_tasks_queue.get()
            if datas["type"] == "list":
                if datas["data"]["msg"]:
                    # await self.package_list_task()
                    await asyncio.gather(*(await self.package_post_comment_task(datas=datas)))
            elif datas["type"] == "post":
                def parser_post(content):
                    content = Selector(text=content)
                    data = {}
                    data["title"] = content.xpath(
                        "//h1[@class='Post-Title']/text()").get()
                    data["content"] = content.xpath(
                        "//div[@class='RichText ztext Post-RichText']//text()").getall()
                parser_post(content=datas["data"])
            elif datas["type"] == "comment":
                def parser_comment(data):
                    for i in data:
                        print(i["content"])
                parser_comment(data=datas["data"]["data"])

    async def package_post_comment_task(self, datas: ListData) -> None:
        post_urls = set()
        comment_urls = set()
        for data in datas["data"]["msg"]:
            post_url = re.findall(
                r"https://zhuanlan.zhihu.com/p/\d+", data)
            post_urls = post_urls | set(post_url)
        comment_urls = [self.comment_url_temp %
                        (post_url.split("/")[-1]) for post_url in post_urls]
        tasks = [
            asyncio.ensure_future(self.newest_tasks_queue.put(
                {
                    "url": post_url,
                    "type": "post"
                }
            ))for post_url in post_urls
        ]+[
            asyncio.ensure_future(self.newest_tasks_queue.put(
                {
                    "url": comment_url,
                    "type": "comment"
                }
            ))for comment_url in comment_urls
        ]
        return tasks

    async def run(self) -> None:
        await self.package_list_task()
        ass = [
            asyncio.ensure_future(self.request_worker(session=session))
            for session in self.sessions
        ]
        bss = [asyncio.ensure_future(self.parser_worker())
               for _ in range(self.parser_worker_num)]
        await asyncio.gather(*ass)
        await asyncio.gather(*bss)
