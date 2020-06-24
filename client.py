import aiohttp
from time import perf_counter
import asyncio
from io import BytesIO
from random import randint
from PIL import Image
import json


post_url = 'http://0.0.0.0:8080/resize'
get_url = 'http://0.0.0.0:8080/get_img?key={}'

keys = []
current_key = 0

async def post_img(url):
    async with aiohttp.ClientSession() as session:
        height, width = randint(400, 1000), randint(600, 1400)
        data = {
            'img': open('im_client/png.png', 'rb'),
            'height': str(height),
            'width': str(width),
        }
        resp  = await session.post(url, data=data)
        # if resp.content_type == ''
        print(f'Response status is {resp.status}')
        data = json.loads(await resp.text())
        if resp.status == 200:
            print('Image sent. Image key is {}. New size is: {}'.format(data['key'], (width, height)))
            keys.append(data['key'])
        else:
            print('Something wrong: {}'.format(data))

async def get_img(url):
    global current_key
    async with aiohttp.ClientSession() as session:
        key = keys[current_key]
        current_key += 1
        print(f'Key is {key}')
        print(f'Waiting for get requset with key: {key}')
        resp = await session.get(url.format(key))
        print(f'Response status is {resp.status}')
        if resp.content_type == 'application/json':
            data = json.loads(await resp.text())
            print('Image with key[{}] is {}'.format(data['key'], data['status']))
        elif resp.content_type in ['image/jpeg', 'image/png']:
            image = Image.open(BytesIO(await resp.read()))
            extension = 'jpg' if resp.content_type == 'image/jpeg' else 'png'
            image.save('im_client/pil_{}.{}'.format(key, extension))
            print(f'Image pil_{key}.jpg saved with size: {image.size}')
        else:
            print(f'Unknown content-type: {resp.content_type}')

async def many_runs(n):
    print(f'Run {n} requests')
    print('----------POST-------------')
    await asyncio.gather(*[post_img(post_url) for _ in range(n)])
    print('----------KEYS-------------')
    print(f'Keys after post request:\n{keys}')
    print('----------GET--------------')
    await asyncio.gather(*[get_img(get_url) for _ in range(n)])

if __name__ == '__main__':
    t = perf_counter()
    asyncio.run(many_runs(1))
    total = perf_counter() - t
    print(f'Total time taken: {total} seconds')
