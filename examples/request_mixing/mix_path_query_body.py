"""
This example serves to show how to do three commons ways to get information
from a request:
1. In the path
2. In query parameters
3. In the body (here as a json)

It also shows how to mix them all together
"""
from typing import Optional, List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class JsonBody(BaseModel):
    """Base model for json body"""
    name: str
    age: int
    height: float
    dimensions: List[float]


@app.get('/path/{source}')
async def path_var(source: str):
    """Get variable from path

    Try with:
    In [4]: src = 'home'
    In [5]: res = requests.get(f'http://127.0.0.1:8000/path/{src}')
    In [6]: assert res.json()
    In [7]: assert res.json()['source'] == src

    """
    return {'source': source}


@app.get('/query_params')
async def query_params(q: str, p: Optional[float] = None):
    """Get variables from query parameters in url

    Try with
    In [13]: res = requests.get(f'http://127.0.0.1:8000/query_params?q=123456')
    In [14]: assert res.json()
    In [15]: assert res.json()['q'] == '123456'
    In [16]: res = requests.get('http://127.0.0.1:8000/query_params?q=a&p=2.0')
    In [17]: assert res.json()
    In [18]: assert res.json()['p'] == 2.0
    """
    return {'q': q, 'p': p or 'unavailable'}


@app.post('/json_body')
async def json_body(body: JsonBody):
    """Json body test

    Try with:
    In [20]: res = requests.post(f'http://127.0.0.1:8000/json_body',
    json={'name': 'Klas', 'age': 32, 'height': 183,
    'dimensions': [1.0, 2.0, 3.0, 4.0]})
    In [21]: res.json()
    Out[21]:
    {'name': 'Klas',
     'age': 32,
     'height': 183.0,
     'dimensions': [1.0, 2.0, 3.0, 4.0]}
    """
    return {
        'name': body.name,
        'age': body.age,
        'height': body.height,
        'dimensions': body.dimensions
    }


@app.post('/mixing/{pathvar}')
async def mixing(pathvar: Optional[str] = None,
                 query_param: Optional[float] = None,
                 body: Optional[JsonBody] = None):
    """Mix it all together

    Try with:
    In [40]: res = \
             requests.post(
             f'http://127.0.0.1:8000/mixing/it_up?query_param=32',
             json={'name': 'Klas', 'age': 32.8, 'height': 183,
             'dimensions': [0.0, 1.0, 2.0, 3.0]})
    In [41]: res.json()
    Out[41]:
    {'path_var': 'it_up',
     'query_param': 32.0,
     'body': {'name': 'Klas',
     'age': 32,
     'height': 183.0,
     'dimensions': [0.0, 1.0, 2.0, 3.0]}}

    """
    return {'path_var': path_var,
            'query_param': query_param,
            'body': body.__dict__ if body else body}
