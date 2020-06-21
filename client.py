import aiohttp
from time import perf_counter
import asyncio
from random import randint
from PIL import Image


url = 'http://0.0.0.0:8080/resize'

async def post_lang(url):
    async with aiohttp.ClientSession() as session:
        data = {
            'img': open('img.jpg', 'rb'),
            'height': str(randint(400, 1000)),
            'width': str(randint(600, 1400)),
        }
        post_data  = await session.post(url, data=data)
        print(await post_data.text())

async def main():
    await asyncio.gather(*[post_lang(url) for _ in range(30)])

if __name__ == '__main__':
    t = perf_counter()
    asyncio.run(main())
    total = perf_counter() - t
    print(f'Total time taken: {total} seconds')
