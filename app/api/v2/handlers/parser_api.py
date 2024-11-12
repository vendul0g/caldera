from aiohttp import web
import os
import aiohttp_apispec

class ParserApi:
    def __init__(self, services):
        self.services = services
        
    def add_routes(self, app: web.Application):
        router = app.router
        router.add_get('/parsers', self.get_parsers)

    @aiohttp_apispec.docs(
        tags=['parsers'],
        summary='Retrieve Available Parsers',
        description='Returns a list of all available parser files located in the stockpile plugin parsers directory.',
        responses={
            200: {
                'description': 'List of parser files in JSON format.',
                'content': {
                    'application/json': {
                        'example': {
                            'parsers': ['example_parser.py', 'another_parser.py']
                        }
                    }
                }
            }
        }
    )
    async def get_parsers(self, request):
        """
        Retrieve a list of available parsers.

        This endpoint scans the 'plugins/stockpile/app/parsers' directory
        and returns all files ending with `.py`.
        """
        parser_list = []
        parser_dir = 'plugins/stockpile/app/parsers'
        for root, dirs, files in os.walk(parser_dir):
            for file in files:
                if file.endswith('.py'):
                    parser_list.append(file)
        return web.json_response({'parsers': parser_list})
