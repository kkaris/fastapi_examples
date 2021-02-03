"""
This example show when to use and when not to use async function definitions

Main gist:
You can only use `await` inside of functions created with `async def`,
however, you CAN create an async def function without using await inside
of it (but that doesn't make much sense)

Some reading
https://fastapi.tiangolo.com/tutorial/dependencies/#to-async-or-not-to-async
https://fastapi.tiangolo.com/async/


Copied from fastapi.tiangolo.com/async/:

"If you are using third party libraries that tell you to call them with
 await, like:

>>> results = await some_library()

 Then, declare your path operation functions with async def like:

>>> @app.get('/')
... async def read_results():
...    results = await some_library()
...    return results

 If you are using a third party library that communicates with something (a
 database, an API, the file system, etc) and doesn't have support for using
 await, (this is currently the case for most database libraries),
 then declare your path operation functions as normally, with just def, like:

>>> @app.get('/')
... def results():
...     results = some_library()
...     return results

 If your application (somehow) doesn't have to communicate with anything
 else and wait for it to respond, use async def. Clarifying note: this means
 that a simple function doing some elementary operation like

>>> def commmon_parameters(q: Optional[str] = None, skip: int = 0,
...                              limit: int = 100):
...     return {'q': q, 'skip': skip, 'limit': limit}

 CAN, and SHOULD, use `async def`:

>>> async def commmon_parameters(q: Optional[str] = None, skip: int = 0,
...                              limit: int = 100):
...     return {'q': q, 'skip': skip, 'limit': limit}

 If you just don't know, use normal def."

"""
import requests
import aiofiles
from typing import Optional
from fastapi import FastAPI


app = FastAPI()


async def read_file_async(fname: str):
    """Reads a file asynchronously"""
    async with aiofiles.open(fname) as f:
        contents = f.read()
    return contents


def read_file_blocking(fname: str):
    """Reads file while blocking"""
    with open(fname, 'r') as f:
        contents = f.read()
    return contents


# This path operation function does not communicate with anything else,
# and should therefore be async-ed
@app.get('/adder')
async def simple_adder(a: int, b: Optional[int] = 0):
    """Adds two numbers"""
    return {'a + b': a + b}


# This path operation function calls an external library that doesn't
# support using await, so define it without async
@app.get('/status_code')
def get_page_status_code(q: str = 'fastapi'):
    """Query duckduckgo.com for a user provided query"""
    res = requests.get('https://api.duckduckgo.com/',
                       params={'q': q,
                               'format': 'json',
                               'pretty': 1})
    return {'status_code': res.status_code}


# This path operation function calls an external library that does support
# using await, so define it with async
@app.get('/file/{fname}')
async def get_file(fname: str):
    cont = await read_file_async(fname)
    return {'content': cont}
