from aiohttp import web
from PIL import Image
from io import BytesIO
from collections import deque
from pathlib import Path


routes = web.RouteTableDef()

async def handler(request):
    return web.Response(text='Async Server in Python 3.8')

# async def add_lang(request):
#     data = await request.post()
#     img = data.get('img').file
#     height, width = int(data.get('height')), int(data.get('width'))
#     image = Image.open(BytesIO(img.read()))
#     image = await resize_image(image, (width, height))
#     image.save('new_img_pil.jpg')

#     # print(img)
#     print(f'Resizing image to size {height}, {width}')
#     return web.Response(text=f'Image was resized to ({height}, {width})')

class ImageResizer:

    def __init__(self):
        self.total_image_count = 0
        self.tasks = deque()

    async def resize_image(self, image, wh):
        print(f'Resizing image to size: {wh}')
        return image.resize(wh)
    
    async def post_view(self, request):
        data = await request.post()
        img = data.get('img').file
        height, width = int(data.get('height')), int(data.get('width'))
        print('Post request. Size: {}'.format((width, height)))

        image = Image.open(BytesIO(img.read()))
        self.tasks.append(self.resize_image(image, (width, height)))
        print(f'Key {len(self.tasks) - 1} added')
        response = {
            'key': len(self.tasks) - 1,
            'status': 'ok',
        }
        return web.json_response(response)
    
    async def get_view(self, request):
        key = request.rel_url.query.get('key', '')
        print(f'Get request: key={key}')
        response = {
            'key': key,
            'status': 'ok',
            'body': {
                'image': await self.tasks[int(key)]
            }
        }
        image = response['body']['image']
        image.save('im_server/pil_{}.jpg'.format(key))
        print(f'Get request: key={key}, imagepath: images/pil_{key}.jpg, with size: {image.size}')
        resp = web.FileResponse(f'im_server/pil_{key}.jpg')

        return resp
        # resp = web.StreamResponse(status=200)
        # await resp.prepare(request)
        # await resp.write(image.tobytes())
        # return resp


async def json_view(requset):
    data = {
        'key': 'key',
        'status': 'ok',
        'body': {
            'hello': 'world',
        }
    }
    return web.json_response(data)

async def initialization():
    print('Starting app')
    app = web.Application()
    resizer = ImageResizer()
    app.add_routes([
        web.post('/resize', resizer.post_view),
        web.get('/get_img', resizer.get_view),
        web.get('/json/{key}', json_view)
    ])
    for name, resource in app.router.named_resources().items():
        print(name, resource)
    return app

web.run_app(initialization())