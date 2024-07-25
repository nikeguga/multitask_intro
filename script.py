import aiohttp
import asyncio
import os
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from urllib.parse import urlparse
import sys

async def download_image(session, url, file_path):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                filename = os.path.basename(urlparse(url).path)
                full_path = os.path.join(file_path, filename)
                with open(full_path, 'wb') as f:
                    f.write(await response.read())
                return url, filename, True
            else:
                return url, None, False
    except Exception as e:
        return url, None, False

def run_in_thread(loop, func, *args):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(func(*args))

def run_in_process(loop, func, *args):
    asyncio.run(func(*args))

async def download_images(urls, file_path):
    os.makedirs(file_path, exist_ok=True)
    async with aiohttp.ClientSession() as session:
        tasks = []
        start_time = time.time()

        # Используем ThreadPoolExecutor для многопоточного выполнения
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            for url in urls:
                tasks.append(loop.run_in_executor(executor, download_image, session, url, file_path))
            results = await asyncio.gather(*tasks)
        
        # Используем ProcessPoolExecutor для многопроцессорного выполнения
        with ProcessPoolExecutor() as executor:
            loop = asyncio.new_event_loop()
            for url in urls:
                tasks.append(loop.run_in_executor(executor, download_image, session, url, file_path))
            results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time

        for url, filename, success in results:
            if success:
                print(f"Downloaded {filename} from {url} to {file_path}")
            else:
                print(f"Failed to download from {url}")

        print(f"Total time: {total_time:.2f} seconds")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        file_path = sys.argv[1]
        urls = sys.argv[2:]
        asyncio.run(download_images(urls, file_path))
    else:
        print("Usage: python script.py <save_directory> <url1> <url2> ...")


#На тест в bash под windows: python script.py "C:\Users\User\Desktop\Multitask_intro\images" https://upload.wikimedia.org/wikipedia/en/d/da/I_Don%27t_Like_It_-_Pauline_Pantsdown_%28album_cover%29.jpg
