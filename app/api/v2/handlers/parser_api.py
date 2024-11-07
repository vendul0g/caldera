from aiohttp import web
import os

class ParserApi:
    def __init__(self, services):
        self.services = services
        
    def add_routes(self, app: web.Application):
        router = app.router
        router.add_get('/parsers', self.get_parsers)

    async def get_parsers(self, request):
        parser_list = []
        # Example of accessing parser modules from a specific directory
        parser_dir = 'plugins/stockpile/app/parsers'
        for root, dirs, files in os.walk(parser_dir):
            for file in files:
                if file.endswith('.py'):
                    parser_list.append(file)
        return web.json_response({'parsers': parser_list})
