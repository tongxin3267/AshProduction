from sanic.views import HTTPMethodView
from sanic.response import text


class ClicksView(HTTPMethodView):
    async def get(self, request):
        return text('I am async get method')
