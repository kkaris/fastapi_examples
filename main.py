"""
Minimum Working Example showing:
 - automated docs
 - data validation
 - async vs threading


run the service using uvicorn (in this directory):
uvicorn main:app --relaod


## Automated Docs
Browse to 'http://localhost:8000/docs' or '.../redoc'

## Data validation
Read more here:
https://fastapi.tiangolo.com/tutorial/path-params/#data-validation
https://pydantic-docs.helpmanual.io/

# Validation in path parameters
https://fastapi.tiangolo.com/tutorial/path-params/

POST to '/items/{item_id}' with {item_id} set to an integer and a
non-integer string. Any non-integer should give 422 error and also tell you
what was wrong with the query.

# Validation in JSON body
https://fastapi.tiangolo.com/tutorial/body/

POST to either of '/post_model_async' or '/post_model_sync' with a json body
conforming to:

>>> {'min': 0, 'max': 5, 'ids': [1, 2, 3, 4]}

Replace e.g. 0 with 'abc' as argument for 'min' or add a string in the 'ids'
list and a 422 error should be returned.


## async vs threading for non-blocking requests

This allows the api to respond to multiple requests, even if any of the
requests takes a long time (> 1 second) to complete. Read more here:
https://fastapi.tiangolo.com/async/

To try it out:

In a new ipython session, run an infinite loop GET-ing requests from '/':
>>> import requests
>>> from time import sleep
>>> while True:
...     res = requests.get('http://localhost:8000'); print(res.status_code)
...     sleep(1)

In a second new ipython session: run requests to '/post_model_async' and
'/post_model_sync' and check how the server handles the queries:
>>> res = requests.post('http://localhost:8000/post_model_async',
...                     json={'min': 0, 'max': 5, 'ids': [1, 2, 3, 4]})
...                     print(res.json())

If everything is working correctly, the infinite loop requesting '/' should
just keep going while the server is working on the POST requests to
'/post_model_async' or '/post_model_sync'.

"""
from time import sleep
from asyncio import sleep as async_sleep
from typing import List

from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()


# With Pydantic's BaseModel we can create a structure capable of data
# validation of its fields and also produce a JSON schema that is used in the
# automated documentation
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
    # Use `def` instead `async def` when the code runs blocking I/O
    # functions, here illustrated with regular sleep(). This function will
    # be run in an external threadpool, allowing the server to continue to
    # continue to repsond to requests on its main thread:
    # https://fastapi.tiangolo.com/async/#path-operation-functions
    sleep(5)
    return my_data

