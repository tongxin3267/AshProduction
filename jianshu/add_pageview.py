import asyncio
from asyncio.queues import Queue
from typing import List
from aiohttp import ClientSession
from parsel import Selector
import click

# static
Articles = List[str]


async def get_articles_by_date(userId: str) -> Articles:
    article_lists = []
    async with ClientSession() as session:
        page = 1
        temp_article_lists = []
        while 1:
            async with session.get(
                    f"https://www.jianshu.com/u/{userId}?order_by=shared_at&page={page}"
            ) as response:
                content = await response.text()
                dom = Selector(text=content)
                article_list = dom.xpath(
                    "//ul[@class='note-list']//a[@class='title']/@href"
                ).getall()
                current_article_lists = [
                    f"https://www.jianshu.com{i}" for i in article_list
                    if "p" in i
                ]
                if current_article_lists != temp_article_lists:
                    temp_article_lists = current_article_lists
                    article_lists.extend(current_article_lists)
                    page += 1
                else:
                    break
    article_lists = set(article_lists)
    return article_lists


async def add_action(session: ClientSession, url: str) -> None:
    """
    According to different articlesID structure request. 
    there are some optimization
    """
    url_sub = url.split("/")[-1]
    data = {
        "uuid": "5e43e1c6-ca97-4787-a033asddasd",
        "referrer": "https://www.jianshu.com"
    }
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0",
        "X-CSRF-Token":
        "+LOfEEblhHerUy77qZvhhWkwiUIYrirND0ofIfYesBLc0WUIhsHwFTTzmE+jprN8Yto50LE79knh3Ao8oq30vg==",
        "Cookie":
        "sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22164f0ee834e42a-06c76e6f7944b38-4c312b7b-1327104-164f0ee834f2ab%22%2C%22%24device_id%22%3A%22164f0ee834e42a-06c76e6f7944b38-4c312b7b-1327104-164f0ee834f2ab%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.baidu.com%2Flink%22%2C%22%24latest_referrer_host%22%3A%22www.baidu.com%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%7D%2C%22first_id%22%3A%22%22%7D; read_mode=day; default_font=font2; locale=zh-CN; _m7e_session=920bfd266a5d73adf6bff486082f84e4; signin_redirect=https%3A%2F%2Fwww.jianshu.com%2Fp%2F4a526bc6276b",
        "Host":
        "www.jianshu.com",
        "Referer":
        f"https://www.jianshu.com/p/{url_sub}",
    }
    url = f"https://www.jianshu.com/notes/{url_sub}/mark_viewed.json"
    try:
        response = await session.post(url, headers=headers, data=data)
        code = response.status
    except Exception:
        # Todo
        pass
    else:
        pass
    finally:
        pass


async def flow(userId: str, interval: int):
    task_q = Queue()
    session = ClientSession()
    asyncio.ensure_future(put_seeds(q=task_q, userId=userId))
    while 1:
        try:
            seed = await task_q.get()
            print(f"get-{seed}")
        except Exception as e:
            print(e)
        else:
            await add_action(session=session, url=seed)
            await task_q.put(seed)
        finally:
            await asyncio.sleep(interval)


async def put_seeds(q: Queue, userId: str):
    current_seeds = set()
    while 1:
        for i in ((await get_articles_by_date(userId=userId)) - current_seeds):
            await q.put(i)
        await asyncio.sleep(18000)


@click.command()
@click.option(
    '--userid', default="e9fdf09df277", help='your jianshu homepageId')
@click.option(
    '--interval', default=5, help='your interval')
def run(userid, interval):
    try:
        import uvloop
    except ImportError as e:
        print("no install uvloop package")
    else:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    finally:
        _loop = asyncio.get_event_loop()
        _loop.run_until_complete(flow(userId=userid,interval=interval))


run()