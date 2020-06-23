from aiohttp import web
import asyncio
from PIL import Image
from io import BytesIO
from pathlib import Path
import mimetypes
from datetime import datetime
from time import time

from logger import FileLogger


class ImageResizer:

    def __init__(self, logger=None):
        self.total_image_count = 0
        self.tasks = []
        self.logger = logger or FileLogger()
        self.logger.log(f'Server started: {datetime.now()}')

    async def resize_image(self, image, wh):
        return image.resize(wh)
    
    async def post_view(self, request):
        data = await request.post()
        self.logger.log(f'Got post request from {request.remote}')
        file_type = mimetypes.guess_type(data.get('img').filename)[0]
        if file_type not in ['image/png', 'image/jpeg']:
            self.logger.log(f'Request from {request.remote} fails: not allowed image extension')
            return web.json_response({'status': 'denied', 'error': 'not allowed image extension'}, status=400)

        img = data.get('img').file
        try: 
            height, width = int(data.get('height')), int(data.get('width'))
        except ValueError:
            self.logger.log(f'Request from {request.remote} fails: height or width is not integer value')
            return web.json_response({'status': 'denied', 'error': 'height or width is not integer value'}, status=400)

        if height <= 0 or width <= 0:
            self.logger.log(f'Request from {request.remote} fails: height or width is not natural numbers')
            return web.json_response({'status': 'denied', 'error': 'height or width is not natural numbers'}, status=400)
        
        self.logger.log('Post request. Size: {}'.format((width, height)))
        
        # self.logger.log(f'Post request')
        image = Image.open(BytesIO(img.read()))
        self.tasks.append(
            asyncio.create_task(self.resize_image(image, (width, height)))
        )
        key = len(self.tasks) - 1
        self.logger.log(f'For request from {request.remote} key {key} added')
        response = {
            'key': key,
            'status': 'ok',
        }
        return web.json_response(response)
    
    async def get_view(self, request):
        key = request.rel_url.query.get('key', '')
        self.logger.log(f'Get request from {request.remote}: key={key}')
        try:
            task = self.tasks[int(key)]
        except IndexError:
            self.logger.log(f'Get request from {request.remote} and key={key} fails: key does not exist')
            return web.json_response({'status': 'denied', 'error': 'key does not exist'}, status=404)
        if task.done():
            image = await task
            image.save('im_server/pil_{}.jpg'.format(key))
            self.logger.log(f'Get request from {request.remote}: key={key}, imagepath: images/pil_{key}.jpg, with size: {image.size}')
            resp = web.FileResponse(f'im_server/pil_{key}.jpg')
        else:
            self.logger.log(f'Get request from {request.remote}: key={key}, image in process')
            resp = web.json_response({'key': key, 'status': 'in process'})

        return resp


async def initialization():
    app = web.Application()
    resizer = ImageResizer()
    app.add_routes([
        web.post('/resize', resizer.post_view),
        web.get('/get_img', resizer.get_view),
    ])
    return app

web.run_app(initialization())