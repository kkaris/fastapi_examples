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
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

