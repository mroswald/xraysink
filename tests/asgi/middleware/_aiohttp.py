"""Helpers for testing an instrumented aiohttp web server."""

import asyncio

from aiohttp import web
from aiohttp.web_exceptions import HTTPUnauthorized
from xraysink.asgi.middleware import xray_middleware


class AioHttpServerFactory(object):
    """
    Factory for an xray-instrumented aiohttp Application's
    that implements our test endpoints.
    """

    __test__ = False

    async def handle_ok(self, request: web.Request) -> web.Response:
        """
        Handle / request
        """
        if "content_length" in request.query:
            headers = {"Content-Length": request.query["content_length"]}
        else:
            headers = None

        return web.Response(text="ok", headers=headers)

    async def handle_client_error(self, request: web.Request) -> web.Response:
        """
        Handle /client_error which returns a 422 client error
        """
        return web.Response(text="bad something something", status=422)

    async def handle_unauthorized(self, request: web.Request) -> web.Response:
        """
        Handle /unauthorized which returns a 401
        """
        raise HTTPUnauthorized()

    async def handle_exception(self, request: web.Request) -> web.Response:
        """
        Handle /exception which raises a KeyError
        """
        return {}["key"]

    async def handle_delay(self, request: web.Request) -> web.Response:
        """
        Handle /delay request
        """
        await asyncio.sleep(0.3)
        return web.Response(text="ok")

    def get_app(self) -> web.Application:
        app = web.Application(middlewares=[xray_middleware])
        app.router.add_get("/", self.handle_ok)
        app.router.add_get("/client_error", self.handle_client_error)
        app.router.add_get("/exception", self.handle_exception)
        app.router.add_get("/unauthorized", self.handle_unauthorized)
        app.router.add_get("/delay", self.handle_delay)

        return app

    @classmethod
    def app(cls) -> web.Application:
        return cls().get_app()