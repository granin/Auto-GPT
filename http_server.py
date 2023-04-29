import asyncio
from aiohttp import web

routes = web.RouteTableDef()

responses = {}


@routes.get('/{key}')
async def get_value(request):
    key = request.match_info['key']
    if key in responses:
        return web.Response(text=responses[key])
    else:
        return web.Response(status=404)


@routes.post('/{key}')
async def set_value(request):
    key = request.match_info['key']
    value = await request.text()
    responses[key] = value
    return web.Response(status=200)


def main():
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host='localhost', port=8080)


if __name__ == "__main__":
    main()
