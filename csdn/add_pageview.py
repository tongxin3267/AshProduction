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
        while 1:
            async with session.get(
                    f"https://blog.csdn.net/{userId}/article/list/{page}"
            ) as response:
                content = await response.text()
                dom = Selector(text=content)
                current_article_list = dom.xpath(
                    "//h4[@class='']/a/@href").getall()
                if current_article_list:
                    article_list = list(
                        set([i for i in current_article_list if userId in i]))
                    article_lists.extend(article_list)
                    page += 1
                else:
                    break
    article_lists = set(article_lists)
    print(len(article_lists))
    return article_lists


async def add_action(session: ClientSession, url: str) -> None:
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
        await session.get(url, headers=headers)
    except Exception as e:
        # Todo
        pass


async def flow(userId: str):
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
            await asyncio.sleep(20)


async def put_seeds(q: Queue, userId: str):
    current_seeds = set()
    while 1:
        for i in ((await get_articles_by_date(userId=userId)) - current_seeds):
            await q.put(i)
        await asyncio.sleep(18000)


@click.command()
@click.option(
    '--userid', default="weixin_43116910", help='your jianshu homepageId')
def run(userid):
    try:
        import uvloop
    except ImportError as e:
        print("no install uvloop package")
    else:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    finally:
        _loop = asyncio.get_event_loop()
        _loop.run_until_complete(flow(userid))


run()