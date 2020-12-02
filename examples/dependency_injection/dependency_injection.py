"""
The dependency 'common_parameters' is called as part of the path
operation function, kind of like a decorator

Here the sole functionality of the dependency is to get the parameters of
the request and return them as a dictionary.

Shared code is one use case, other use cases are e.g. shared database
connections and enforcing security, authentication, role requirements, etc.

From the docs:
  To async or not to async?
  As dependencies will also be called by FastAPI (the same as your path
  operation functions), the same rules apply while defining your functions.

  You can use async def or normal def.

  And you can declare dependencies with async def inside of normal def path
  operation functions, or def dependencies inside of async def path operation
  functions, etc.

Run this as a server using uvicorn with:
> uvicorn dependency_injection.dependency_injection:app --reload

from the examples directory.
"""
from typing import Optional

from fastapi import Depends, FastAPI

app = FastAPI()


async def commmon_parameters(q: Optional[str] = None, skip: int = 0,
                             limit: int = 100):
    return {'q': q, 'skip': skip, 'limit': limit}


@app.get('/items/')
async def read_items(commons: dict = Depends(commmon_parameters)):
    return commons


@app.get('/users/')
async def read_users(commons: dict = Depends(commmon_parameters)):
    return commons
