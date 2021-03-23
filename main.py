from time import sleep
from asyncio import sleep as async_sleep
from typing import List

from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()


class MyData(BaseModel):
    min: float
    max: float
    ids: List[int]


@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.post('/items/{item_id}')
async def read_item(item_id: int):
    return {'item_id': item_id}


@app.post('/post_model_async', response_model=MyData)
async def read_item(my_data: MyData):
    # Runs async/awaitable code
    await async_sleep(5)
    return my_data


@app.post('/post_model_sync', response_model=MyData)
def read_item(my_data: MyData):
    # No 'async def', runs synchronous code
    sleep(5)
    return my_data

