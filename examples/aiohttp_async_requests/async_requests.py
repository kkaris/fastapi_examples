"""
Provides and example of how to use the aiohttp library to perform
asynchronous requests

The example assumes the server needs to make an http request to e.g. another
service running locally

See docs for aiohttp at:
https://github.com/aio-libs/aiohttp
"""
import aiohttp
import asyncio
from typing import Optional, Dict
from fastapi import FastAPI

app = FastAPI()


async def search_ddg(search: str) -> Dict:
    """Search duckduckgo"""
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.duckduckgo.com/',
                               params={'q': search,
                                       'format': 'json',
                                       'pretty': 1}) as response:
            print(f'Status: {response.status}')
            print(f'Content-type: {response.headers["content-type"]}')
            json_resp = await response.json()

    return json_resp


@app.get('/search_ddg')
async def search_ddg(search_str: str = 'fastapi'):
    resp_json = await search_ddg(search_str)
    return resp_json


@app.get('/health')
async def health():
    return {'status': 'pass'}
