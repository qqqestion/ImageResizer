from aiohttp import web
import asyncio
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from pathlib import Path
import mimetypes
from datetime import datetime
from time import time
import os

from logger import FileLogger


class ImageResizer:

    def __init__(self, logger=None):
        self.request_count = 0
        self.tasks = {}
        self.logger = logger or FileLogger()
        self.logger.log(f'Server started: {datetime.now()}')

    async def resize_image(self, image, wh):
        return image.resize(wh)
    
    async def receive_data(self, request):
        data = await request.post()
        self.logger.log(f'Got post request from {request.remote}')
        file_type = mimetypes.guess_type(data.get('img').filename)[0]
        if file_type not in ['image/png', 'image/jpeg']:
            raise RuntimeError(f'not allowed image extension.')
        file_extension = file_type.replace('image/', '')

        try: 
            height, width = int(data.get('height', '')), int(data.get('width', ''))
        except ValueError:
            raise RuntimeError(f'height or width is not integer value.')

        if height <= 0 or width <= 0:
            raise RuntimeError('height or width is not natural numbers.')
        img = data.get('img').file
        try: 
            image = Image.open(BytesIO(img.read()))
        except UnidentifiedImageError:
            raise RuntimeError(f'can\'t get image.')
        return image, file_extension, width, height
    
    async def post_view(self, request):
        try:
            image, extension, width, height = await self.receive_data(request)
        except RuntimeError as e:
            message = f'Request from {request.remote} fails: {repr(e)}'
            self.logger.log(message)
            return web.json_response({'status': 'denied', 'errror': message}, status=400)
        except Exception as e:
            message = f'Request from {request.remote} fails: {repr(e)}'
            self.logger.log(message)
            return web.json_response({'status': 'denied', 'error': 'Server got error. Please try again.'}, status=400)

        self.logger.log('Post request from {} new task: size={}'.format(request.remote, (width, height)))
        
        self.request_count += 1
        key = self.request_count
        self.tasks[key] = (
            asyncio.create_task(self.resize_image(image, (width, height))),
            extension
        )
        self.logger.log(f'Post request from {request.remote}new key: {key}')
        return web.json_response({'status': 'ok', 'key': key})
    
    async def get_view(self, request):
        key = request.rel_url.query.get('key', '')
        self.logger.log(f'Get request from {request.remote}: key={key}')
        try:
            key = int(key)
            task, file_extension = self.tasks[key]
        except (ValueError, KeyError):
            self.logger.log(f'Get request from {request.remote} and key={key} fails: key does not exist')
            return web.json_response({'status': 'denied', 'error': 'key does not exist'}, status=404)
        if task.done():
            image = await task
            filename = 'im_server/pil_{}.{}'.format(key, file_extension)
            self.logger.log(f'Get request from {request.remote}: key={key}, imagepath: {filename}, with size: {image.size}')
            image.save(filename)
            resp = web.FileResponse(filename)
            del self.tasks[key]
            # await resp.prepare(request)
            # os.remove(f'im_server/pil_{key}.jpg')
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