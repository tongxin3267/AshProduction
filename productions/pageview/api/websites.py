from sanic.views import HTTPMethodView
from sanic.response import json


class WebsitesView(HTTPMethodView):
    async def get(self, request, **params):
        return text('I am async get method')

    async def post(self, request, **params):
        post_info = request.json
        website = post_info.get("website", None)
        userid = post_info.get("userid", None)
        if not all([website, userid]):
            return json({"error": 1})
        return json({"website": website, "userid": userid})
