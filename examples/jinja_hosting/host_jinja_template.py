"""This example shows how to host a jinja2 template

See more here:
https://fastapi.tiangolo.com/advanced/templates/

As always, run by:
uvicorn jinja_hosting.host_jinja_template:app --reload
"""
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
STATIC = Path(__file__).parent.absolute().joinpath('static')
TEMPLATES = Path(__file__).parent.absolute().joinpath('templates')


# Serve the static files
app.mount('/static', StaticFiles(directory=STATIC.as_posix()), name='static')

# Serve the template to Jinja
templates = Jinja2Templates(directory=TEMPLATES)


# Tell app that response is HTML
@app.get('/items/{id}', response_class=HTMLResponse)
async def read_items(request: Request, id: str):
    return templates.TemplateResponse('item.html', {'request': request,
                                                    'id': id})
