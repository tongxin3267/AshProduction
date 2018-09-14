from typing import Dict, List, Coroutine
import asyncio
from asyncio.locks import Lock
from asyncio.queues import Queue
import ujson
from aiohttp import ClientSession
from aiohttp.client_exceptions import ContentTypeError
import re
from parsel import Selector
from motor.motor_asyncio import AsyncIOMotorClient
from zhihu.corpus.headers import (
    lheaders, cheaders, rheaders, pheaders
)
Params = Dict[str, str]
Sessions = List[ClientSession]
ListData = Dict[str, List or str]
Tasks = List[Coroutine]


class ZhihuCrawler:
    def __init__(self, startup_num: int = 1, request_worker_num: int = 10, parser_worker_num: int = 1):
        self.startup_num = startup_num
        self.request_worker_num = request_worker_num
        self.parser_worker_num = parser_worker_num
        self.newest_tasks_queue = Queue()
        self.waiting_tasks_queue = Queue()
        self._session_list = None
        self.explore_url = "https://www.zhihu.com/node/ExploreRecommendListV2"
        self.lheaders = lheaders
        self.pheaders = pheaders
        self.cheaders = cheaders
        self.rheaders = rheaders
        self.offset = 0
        self.offset_lock = Lock()
        self.comment_url_temp = f"https://www.zhihu.com/api/v4/articles/%s/comments?include=data[*].author,collapsed,reply_to_author,disliked,content,voting,vote_count,is_parent_author,is_author,algorithm_right&order=normal&limit=100&offset=0&status=open"
        self.recommendation_url_temp = f"https://www.zhihu.com/api/v4/articles/%s/recommendation?include=data[*].article.column&limit=100&offset=0"
        client = AsyncIOMotorClient(['127.0.0.1:27000'])
        self.db = client.zhihu

    @property
    def params(self) -> Params:
        return {
            "method": "next",
            "params": ujson.dumps(
                {'limit': 100, 'offset': self.offset})
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
                    "data": json_data,
                }
            elif newest_task["type"] == "post":
                response = await session.get(headers=self.pheaders, url=newest_task["url"])
                text_data = await response.text()
                data = {
                    "id": newest_task["id"],
                    "type": "post",
                    "data": text_data
                }
            elif newest_task["type"] == "comment":
                response = await session.get(headers=self.cheaders, url=newest_task["url"])
                try:
                    json_data = await response.json()
                except ContentTypeError:
                    continue
                data = {
                    "id": newest_task["id"],
                    "type": "comment",
                    "data": json_data
                }
            elif newest_task["type"] == "recommendation":
                response = await session.get(headers=self.rheaders, url=newest_task["url"])
                try:
                    json_data = await response.json()
                except ContentTypeError:
                    continue
                data = {
                    "id": newest_task["id"],
                    "type": "recommendation",
                    "data": json_data
                }
            await self.waiting_tasks_queue.put(data)

    async def parser_worker(self) -> None:
        while 1:
            datas = await self.waiting_tasks_queue.get()
            if datas["type"] == "list":
                if datas["data"]["msg"]:
                    await self.package_list_task()
                    await asyncio.gather(*(await self.package_sub_task(datas=datas)))
            elif datas["type"] == "post":
                def parser_post(content):
                    content = Selector(text=content)
                    data = {}
                    data["title"] = content.xpath(
                        "//h1[@class='Post-Title']/text()").get()
                    data["content"] = content.xpath(
                        "//div[@class='RichText ztext Post-RichText']//text()").getall()
                    return data
                post_data = parser_post(content=datas["data"])
                filter_data = {"id": datas["id"]}
                await self.db.post.update_one(filter_data, {'$set': post_data}, upsert=True)
            elif datas["type"] == "comment":
                def parser_comment(data):
                    return [
                        {
                            "comment": i["content"]
                        } for i in data
                    ]
                comment_data = parser_comment(data=datas["data"]["data"])
                filter_data = {"id": datas["id"]}
                await self.db.post.update_one(filter_data, {'$set': {"comment": comment_data}}, upsert=True)
            elif datas["type"] == "recommendation":
                def parser_recommendation(data):
                    return [
                        {
                            "excerpt": i["article"]["excerpt"],
                            "title": i["article"]["title"],
                        } for i in data
                    ]
                recommendation_data = parser_recommendation(
                    data=datas["data"]["data"])
                filter_data = {"id": datas["id"]}
                await self.db.post.update_one(filter_data, {'$set': {"recommendation": recommendation_data}}, upsert=True)

    async def package_sub_task(self, datas: ListData) -> Tasks:
        post_urls = set()
        for data in datas["data"]["msg"]:
            post_url = re.findall(
                r"https://zhuanlan.zhihu.com/p/\d+", data)
            post_urls = post_urls | set(post_url)
        ids = [post_url.split("/")[-1] for post_url in post_urls]
        comment_urls = [self.comment_url_temp %
                        (post_url.split("/")[-1]) for post_url in post_urls]
        recommendation_urls = [self.recommendation_url_temp %
                               (post_url.split("/")[-1]) for post_url in post_urls]
        tasks = [
            asyncio.ensure_future(self.newest_tasks_queue.put(
                {
                    "id": ids[index],
                    "url": post_url,
                    "type": "post"
                }
            ))for index, post_url in enumerate(post_urls)
        ]+[
            asyncio.ensure_future(self.newest_tasks_queue.put(
                {
                    "id": ids[index],
                    "url": comment_url,
                    "type": "comment"
                }
            ))for index, comment_url in enumerate(comment_urls)
        ]+[
            asyncio.ensure_future(self.newest_tasks_queue.put(
                {
                    "id": ids[index],
                    "url": recommendation_url,
                    "type": "recommendation"
                }
            ))for index, recommendation_url in enumerate(recommendation_urls)
        ]
        return tasks

    async def startup(self) -> None:
        startups = [
            asyncio.ensure_future(self.package_list_task()) for _ in range(self.startup_num)
        ]
        await asyncio.gather(*startups)

    async def run(self) -> None:
        await self.startup()
        request_workers = [
            asyncio.ensure_future(self.request_worker(session=session))
            for session in self.sessions
        ]
        parser_workers = [asyncio.ensure_future(self.parser_worker())
                          for _ in range(self.parser_worker_num)]
        await asyncio.gather(*request_workers)
        await asyncio.gather(*parser_workers)
