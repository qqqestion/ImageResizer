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
            'img': open('im_client/origin.jpg', 'rb'),
            'height': str(height),
            'width': str(width),
        }
        post_data  = await session.post(url, data=data)
        data = json.loads(await post_data.text())
        print('Image sent. Image key is {}. New size is: {}'.format(data['key'], (width, height)))
        keys.append(data['key'])

async def get_img(url):
    global current_key
    async with aiohttp.ClientSession() as session:
        key = keys[current_key]
        current_key += 1
        print(f'Key is {key}')
        print(f'Waiting for get requset with key: {key}')
        resp  = await session.get(url.format(key))
        # print(response.data())

        # print(resp.__dict__)
        image = Image.open(BytesIO(await resp.read()))
        # async with resp:
        #     image = Image.open(BytesIO(await resp.read()))
        image.save(f'im_client/pil_{key}.jpg')
        print(f'Image pil_{key}.jpg saved with size: {image.size}')

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
    asyncio.run(many_runs(2))
    # asyncio.run(one_run())
    total = perf_counter() - t
    print(f'Total time taken: {total} seconds')
