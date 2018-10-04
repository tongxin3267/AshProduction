from sanic import Sanic
from sanic_session import Session, InMemorySessionInterface


def run():
    app = Sanic('PageView')

    def config_extensions():
        session = Session(app, interface=InMemorySessionInterface())

    def config_route():
        from api.clicks import ClicksView
        from api.websites import WebsitesView
        app.add_route(ClicksView.as_view(), '/clicks')
        app.add_route(WebsitesView.as_view(), '/websites')

    config_route()
    config_extensions()
    app.run(host="0.0.0.0", port=8000)

run()