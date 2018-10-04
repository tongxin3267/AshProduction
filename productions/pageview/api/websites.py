from collections import defaultdict
from typing import List
from aiohttp import web
from aiohttp.web import (json_response, RouteTableDef)
from handles import (jianshu_lst, csdn_lst)

websites = RouteTableDef()


@websites.view('/websites')
class WebsitesView(web.View):
    async def get(self):
        return json_response()

    async def post(self):
        post_info = await self.request.json()
        website = post_info.get("website", None)
        userid = post_info.get("userid", None)
        if not all([website, userid]):
            return json_response({"error": 1})
        if not self.request.app["websites"]:
            self.request.app["websites"] = defaultdict(list)
        websites_store = self.request.app["websites"]
        articles = await self.get_articles(website=website, uid=userid)
        websites_store[website].append({
            "userid": userid,
            "articles": articles
        })
        return json_response({"session": self.request.app["websites"]})

    async def get_articles(self, website: str, uid: str) -> List[str]:
        handles = {"jianshu": jianshu_lst, "csdn": csdn_lst}
        return await handles[website](pages=10, uid=uid)
