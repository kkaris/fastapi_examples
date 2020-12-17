"""
This example show when to use and when not to use async function definitions

Main gist:
You can only use `await` inside of functions created with `async def`

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

Todo:
 - Add example of endpoint that has to be run with just `def`
 - Add example of endpoint where it doesn't matter
 - Add example of endpoint where `async def` should/must be used
"""
