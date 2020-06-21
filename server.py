from aiohttp import web
from PIL import Image
from io import BytesIO


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

    async def resize_image(self, image, wh):
        return image.resize(wh)
    
    async def resize_view(self, request):
        data = await request.post()
        img = data.get('img').file
        height, width = int(data.get('height')), int(data.get('width'))

        image = Image.open(BytesIO(img.read()))
        image = await self.resize_image(image, (width, height))
        image.save('images/pil_{}.jpg'.format(self.total_image_count))

        self.total_image_count += 1
        print(f'Resizing image to size {height}, {width}')
        return web.Response(text=f'Image was resized to ({height}, {width})')


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
    app = web.Application()
    resizer = ImageResizer()
    app.add_routes([
        web.post('/resize', resizer.resize_view),
        web.get('/json/{key}', json_view)
    ])
    for name, resource in app.router.named_resources().items():
        print(name, resource)
    return app

web.run_app(initialization())