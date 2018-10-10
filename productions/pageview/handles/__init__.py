from typing import List
from aiohttp import ClientSession
from parsel import Selector


async def jianshu_lst(pages: int, uid: str) -> List[str]:
    article_lists = []
    async with ClientSession() as session:
        for page in range(pages):
            async with session.get(
                    f"https://www.jianshu.com/u/{uid}?order_by=shared_at&page={page}"
            ) as response:
                content = await response.text()
                dom = Selector(text=content)
                article_list = dom.xpath("//ul[@class='note-list']//a[@class='title']/@href").getall()
                article_list = [
                    f"https://www.jianshu.com{i}" for i in article_list if "p" in i
                ]
                article_lists.extend(article_list)
    article_lists = list(set(article_lists))
    return article_lists


async def csdn_lst(pages: int, uid: str) -> List[str]:
    article_lists = []
    async with ClientSession() as session:
        for page in range(pages):
            async with session.get(
                    f"https://blog.csdn.net/{uid}/article/list/{page}"
            ) as response:
                content = await response.text()
                dom = Selector(text=content)
                article_list = dom.xpath("//h4[@class='']/a/@href").getall()
                article_list = list(set([i for i in article_list if uid in i]))
                article_lists.extend(article_list)
    return article_lists


async def csdn_add_page_view(session: ClientSession, url: str):
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
    except Exception:
        # Todo
        pass


async def jianshu_add_page_view(session: ClientSession, url: str):
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