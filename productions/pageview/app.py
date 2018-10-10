import asyncio
from collections import defaultdict
from pprint import pprint
from aiohttp.web import Application
from aiohttp import web
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pprint("no uvloop")
finally:
    loop = asyncio.get_event_loop()

app = Application()


async def run(app):
    def config_routes(app):
        from api.websites import websites
        app.add_routes(websites)

    def config_tasks(app):
        async def _add_page_view(app):
            from backend_tasks.add_page_view import add_page_view
            app.loop.create_task(add_page_view(app))

        app.on_startup.append(_add_page_view)

    def config_static(app):
        app["websites"] = defaultdict(list)

    config_routes(app)
    config_tasks(app)
    config_static(app)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()


asyncio.ensure_future(run(app=app))
loop.run_forever()
